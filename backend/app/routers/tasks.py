import re
from urllib.parse import quote_plus

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..assist import plan_task
from ..database import get_db
from ..deps import get_current_user
from ..models import Category, Item, Location, User
from ..schemas import TaskPlanRequest, TaskPlanResponse, TaskToolNeed

router = APIRouter(prefix="/tasks", tags=["tasks"])

_STOP = {"a", "an", "the", "of", "and", "pair", "set"}


def _keywords(name: str) -> list[str]:
    toks = re.findall(r"[a-zA-Z0-9]+", name.lower())
    return [t for t in toks if t not in _STOP] or toks


def _find_owned(db: Session, user: User, tool_name: str) -> Item | None:
    """Best-effort match of a required tool name against the user's inventory.

    Requires ALL keywords of the tool name to appear in the item name (so
    "Torque wrench" doesn't match a plain "Lug wrench"), with a category whose
    name contains the full tool name as a secondary match.
    """
    keywords = _keywords(tool_name)
    if not keywords:
        return None
    q = db.query(Item).filter(Item.owner_id == user.id, Item.deleted_at.is_(None))

    name_match = q.filter(*[Item.name.ilike(f"%{kw}%") for kw in keywords])
    item = name_match.order_by(Item.status == "available").first()
    if item:
        return item

    # Fall back to a category that matches the whole tool name.
    cat_ids = [
        c.id for c in db.query(Category).filter(Category.name.ilike(f"%{tool_name}%"))
    ]
    if cat_ids:
        return (
            q.filter(Item.category_id.in_(cat_ids))
            .order_by(Item.status == "available")
            .first()
        )
    return None


@router.post("/plan", response_model=TaskPlanResponse)
def plan(
    payload: TaskPlanRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Given a natural-language task, return the tools it needs (matched against
    the user's inventory), step-by-step instructions, safety tips and a video."""
    task = payload.task.strip()
    if not task:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Describe a task")

    plan_data, engine = plan_task(task)

    loc_cache: dict[str, str | None] = {}

    def loc_name(loc_id: str | None) -> str | None:
        if not loc_id:
            return None
        if loc_id not in loc_cache:
            loc = db.get(Location, loc_id)
            loc_cache[loc_id] = loc.name if loc else None
        return loc_cache[loc_id]

    tools: list[TaskToolNeed] = []
    missing_essential = 0
    missing_total = 0
    for t in plan_data.get("required_tools", []):
        name = str(t.get("name", "Tool"))
        essential = bool(t.get("essential", False))
        owned_item = _find_owned(db, user, name)
        owned = owned_item is not None
        if not owned:
            missing_total += 1
            if essential:
                missing_essential += 1
        tools.append(
            TaskToolNeed(
                name=name,
                category=str(t.get("category", "")),
                essential=essential,
                owned=owned,
                location_name=loc_name(owned_item.location_id) if owned_item else None,
                item_id=owned_item.id if owned_item else None,
            )
        )

    video_query = plan_data.get("video_query") or f"how to {task}"

    return TaskPlanResponse(
        task=task,
        title=plan_data.get("title", task),
        tools=tools,
        steps=plan_data.get("steps", []),
        safety=plan_data.get("safety", []),
        ready=missing_essential == 0,
        missing_essential=missing_essential,
        missing_total=missing_total,
        video_query=video_query,
        video_url=f"https://www.youtube.com/results?search_query={quote_plus(video_query)}",
        engine=engine,
    )
