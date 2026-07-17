from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.errand import Errand
from app.models.person import Person
from app.models.place import Place
from app.models.user import User
from app.schemas.errand import ErrandOut
from app.schemas.place import PlaceOut
from app.services.location import PLACE_TYPES, haversine_km

router = APIRouter(prefix="/api/nearby", tags=["nearby"])


def _errands_for_type(place_type: str, user: User, db: Session) -> list[ErrandOut]:
    rows = db.scalars(
        select(Errand).where(
            Errand.owner_id == user.id,
            Errand.place_type == place_type,
            Errand.completed.is_(False),
        )
    )
    out = []
    for e in rows:
        item = ErrandOut.model_validate(e)
        if e.person_id:
            person = db.get(Person, e.person_id)
            item.person_name = person.name if person else None
        out.append(item)
    return out


@router.get("/place-types")
def place_types() -> list[str]:
    """The place-type vocabulary the UI offers for check-in."""
    return PLACE_TYPES


@router.get("")
def nearby(
    lat: float = Query(...),
    lng: float = Query(...),
    radius_km: float = Query(default=5.0, gt=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """GPS entry point (Phase 10).

    Given the device's coordinates, finds saved places within `radius_km` and
    surfaces the errands whose place_type matches, plus any contacts based
    nearby.
    """
    places = list(db.scalars(select(Place).where(Place.owner_id == user.id)))
    people = list(db.scalars(select(Person).where(Person.owner_id == user.id)))

    nearby_places = []
    seen_types: set[str] = set()
    for p in places:
        if p.latitude is None or p.longitude is None:
            continue
        dist = haversine_km(lat, lng, p.latitude, p.longitude)
        if dist <= radius_km:
            seen_types.add(p.place_type)
            nearby_places.append(
                {
                    "place": PlaceOut.model_validate(p).model_dump(),
                    "distance_km": round(dist, 2),
                    "errands": [
                        e.model_dump() for e in _errands_for_type(p.place_type, user, db)
                    ],
                }
            )
    nearby_places.sort(key=lambda x: x["distance_km"])

    nearby_people = []
    for person in people:
        if person.latitude is None or person.longitude is None:
            continue
        dist = haversine_km(lat, lng, person.latitude, person.longitude)
        if dist <= radius_km:
            nearby_people.append(
                {
                    "person_id": person.id,
                    "name": person.name,
                    "location_label": person.location_label,
                    "distance_km": round(dist, 2),
                }
            )
    nearby_people.sort(key=lambda x: x["distance_km"])

    return {
        "location": {"lat": lat, "lng": lng},
        "radius_km": radius_km,
        "nearby_places": nearby_places,
        "nearby_people": nearby_people,
        "matched_place_types": sorted(seen_types),
    }


@router.get("/check-in")
def check_in(
    place_type: str = Query(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Manual entry point (Phase 10).

    The user says "I'm at a <place_type>" and gets the relevant errands plus
    any saved places of that type.
    """
    saved = db.scalars(
        select(Place).where(
            Place.owner_id == user.id, Place.place_type == place_type
        )
    )
    return {
        "place_type": place_type,
        "errands": [e.model_dump() for e in _errands_for_type(place_type, user, db)],
        "saved_places": [PlaceOut.model_validate(p).model_dump() for p in saved],
    }
