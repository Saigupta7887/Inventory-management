import io

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import Response
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from ..audit import log_audit
from ..auth import decode_token
from ..config import get_settings
from ..database import get_db
from ..deps import bearer_scheme, get_current_user
from ..models import Category, Detection, Item, Photo, User
from ..schemas import AcceptDetectionsRequest, DetectionOut, ItemOut, PhotoOut
from ..storage import get_storage
from ..vision import detect_tools

router = APIRouter(prefix="/photos", tags=["photos"])
settings = get_settings()

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_UPLOAD_BYTES = 15 * 1024 * 1024  # 15 MB


def _owned_photo(db: Session, photo_id: str, user: User) -> Photo:
    photo = db.get(Photo, photo_id)
    if photo is None or photo.deleted_at is not None or photo.owner_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Photo not found")
    return photo


def _thumb_key(storage_key: str) -> str:
    root, _, ext = storage_key.rpartition(".")
    return f"{root}_thumb.jpg" if root else f"{storage_key}_thumb.jpg"


def _resolve_photo(db: Session, photo_id: str, token: str | None) -> Photo:
    """Resolve a photo for an <img> request. Accepts a session OR media token
    (media tokens are short-lived and used only in image URLs)."""
    user_id = decode_token(token, scopes={"session", "media"}) if token else None
    if user_id is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")
    photo = db.get(Photo, photo_id)
    if photo is None or photo.deleted_at is not None or photo.owner_id != user_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Photo not found")
    return photo


@router.post("", response_model=PhotoOut, status_code=status.HTTP_201_CREATED)
def upload_photo(
    file: UploadFile = File(...),
    location_id: str | None = Form(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    content_type = file.content_type or "image/jpeg"
    if content_type not in ALLOWED_TYPES:
        raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "Unsupported image type")

    data = file.file.read()
    if not data:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Empty file")
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "Image too large (max 15 MB)")

    storage = get_storage()
    photo = Photo(
        owner_id=user.id,
        location_id=location_id or None,
        content_type=content_type,
        status="uploaded",
    )
    ext = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp", "image/gif": "gif"}[content_type]
    photo.storage_key = f"{photo.id}.{ext}"

    storage.save(photo.storage_key, data, content_type)

    # Best-effort image dimensions + a small thumbnail for fast grids.
    try:
        from PIL import Image

        with Image.open(io.BytesIO(data)) as img:
            photo.width, photo.height = img.size
            thumb = img.convert("RGB")
            thumb.thumbnail((480, 480))
            buf = io.BytesIO()
            thumb.save(buf, "JPEG", quality=82)
            storage.save(_thumb_key(photo.storage_key), buf.getvalue(), "image/jpeg")
    except Exception:
        pass

    db.add(photo)
    db.flush()
    log_audit(db, entity_type="photo", entity_id=photo.id, actor_user_id=user.id, action="create")
    db.commit()
    db.refresh(photo)
    return photo


@router.get("/{photo_id}/file")
def get_photo_file(
    photo_id: str,
    t: str | None = None,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
):
    # Accept the token from the Authorization header OR a `t` query param, so
    # the image can be shown directly in an <img> tag (which can't set headers).
    token = credentials.credentials if credentials else t
    photo = _resolve_photo(db, photo_id, token)
    storage = get_storage()
    if not storage.exists(photo.storage_key):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "File missing")
    return storage.response(photo.storage_key, photo.content_type)


@router.get("/{photo_id}/thumb")
def get_photo_thumb(
    photo_id: str,
    t: str | None = None,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
):
    """Serve the small thumbnail (falls back to the original if none exists)."""
    token = credentials.credentials if credentials else t
    photo = _resolve_photo(db, photo_id, token)
    storage = get_storage()
    thumb_key = _thumb_key(photo.storage_key)
    if storage.exists(thumb_key):
        return storage.response(thumb_key, "image/jpeg")
    if not storage.exists(photo.storage_key):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "File missing")
    return storage.response(photo.storage_key, photo.content_type)


@router.post("/{photo_id}/detect", response_model=list[DetectionOut])
def detect(photo_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Run vision detection on the photo and store pending detections."""
    photo = _owned_photo(db, photo_id, user)
    storage = get_storage()
    if not storage.exists(photo.storage_key):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "File missing")

    photo.status = "processing"
    db.commit()

    image_bytes = storage.read(photo.storage_key)

    results, engine = detect_tools(image_bytes, photo.content_type)

    # Clear any previous pending detections for a clean re-run.
    db.query(Detection).filter(
        Detection.photo_id == photo.id, Detection.status == "pending"
    ).delete()

    created: list[Detection] = []
    for r in results:
        det = Detection(
            photo_id=photo.id,
            label=str(r.get("label", "Unknown tool"))[:160],
            suggested_category=str(r.get("category", ""))[:120],
            confidence=float(r.get("confidence", 0.0) or 0.0),
            bbox=r.get("bbox"),
            status="pending",
        )
        db.add(det)
        created.append(det)

    photo.status = "processed"
    log_audit(
        db, entity_type="photo", entity_id=photo.id, actor_user_id=user.id,
        action="detect", diff={"engine": engine, "count": len(created)},
    )
    db.commit()
    for d in created:
        db.refresh(d)
    return created


@router.get("/{photo_id}/detections", response_model=list[DetectionOut])
def list_detections(photo_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    photo = _owned_photo(db, photo_id, user)
    return db.query(Detection).filter(Detection.photo_id == photo.id).all()


@router.post("/{photo_id}/accept", response_model=list[ItemOut])
def accept_detections(
    photo_id: str,
    payload: AcceptDetectionsRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Turn confirmed detections into real inventory items."""
    photo = _owned_photo(db, photo_id, user)
    location_id = payload.location_id or photo.location_id

    detections = (
        db.query(Detection)
        .filter(Detection.photo_id == photo.id, Detection.id.in_(payload.detection_ids))
        .all()
    )
    if not detections:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No matching detections")

    created_items: list[Item] = []
    for det in detections:
        if det.status == "accepted":
            continue
        category_id = None
        if det.suggested_category:
            cat = (
                db.query(Category)
                .filter(Category.name == det.suggested_category, Category.deleted_at.is_(None))
                .first()
            )
            if cat is None:
                cat = Category(name=det.suggested_category, is_global=False, owner_id=user.id)
                db.add(cat)
                db.flush()
            category_id = cat.id

        item = Item(
            owner_id=user.id,
            name=det.label,
            category_id=category_id,
            location_id=location_id,
            primary_photo_id=photo.id,
            source_detection_id=det.id,
            status="available",
        )
        db.add(item)
        db.flush()
        det.status = "accepted"
        det.item_id = item.id
        log_audit(
            db, entity_type="item", entity_id=item.id, actor_user_id=user.id,
            action="create", diff={"from_detection": det.id},
        )
        created_items.append(item)

    db.commit()
    for it in created_items:
        db.refresh(it)
    return created_items
