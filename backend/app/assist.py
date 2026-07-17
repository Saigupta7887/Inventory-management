"""Task assistant: given a natural-language job ("change my tires"), return the
tools it needs, step-by-step instructions, safety tips and a how-to video query.

Uses Claude when ANTHROPIC_API_KEY is set; otherwise falls back to a small
built-in knowledge base + a generic plan, so the feature works end to end
without any credentials. The router then cross-references the required tools
against the user's own inventory.
"""

import json
import re

from .config import get_settings

settings = get_settings()

PLAN_PROMPT = (
    "A user wants to complete a hands-on task at home. Produce a practical plan.\n"
    'Return ONLY a JSON object with keys:\n'
    '  "title": a short title for the task,\n'
    '  "required_tools": array of objects {"name": short tool name, '
    '"category": broad category, "essential": true/false},\n'
    '  "steps": array of short step strings, in order,\n'
    '  "safety": array of short safety tips,\n'
    '  "video_query": a good YouTube search phrase for a how-to video.\n'
    "Keep tool names simple and generic so they can be matched to an inventory "
    "(e.g. \"Car jack\", \"Lug wrench\", \"Screwdriver\"). No prose outside the JSON.\n\n"
    "Task: "
)

# ---- Built-in knowledge base for common tasks (used when no API key) ----
KB = {
    ("tire", "tyre", "wheel"): {
        "title": "Change a car tire",
        "required_tools": [
            {"name": "Car jack", "category": "Automotive", "essential": True},
            {"name": "Lug wrench", "category": "Wrench", "essential": True},
            {"name": "Spare tire", "category": "Automotive", "essential": True},
            {"name": "Wheel wedges", "category": "Automotive", "essential": False},
            {"name": "Gloves", "category": "Safety", "essential": False},
            {"name": "Flashlight", "category": "Electrical", "essential": False},
            {"name": "Torque wrench", "category": "Wrench", "essential": False},
        ],
        "steps": [
            "Park on firm, level ground and switch on your hazard lights.",
            "Engage the parking brake and place wheel wedges against the tires.",
            "Loosen (don't remove) the lug nuts with the lug wrench about a half turn.",
            "Position the jack under the vehicle's jack point and raise until the flat tire is off the ground.",
            "Fully unscrew the lug nuts and pull the flat tire straight off.",
            "Mount the spare tire onto the bolts and hand-tighten the lug nuts.",
            "Lower the vehicle so the spare touches the ground, then fully tighten the lug nuts in a star pattern.",
            "Lower the vehicle completely and remove the jack.",
            "Torque the lug nuts to spec, stow the flat, and check the spare's pressure.",
        ],
        "safety": [
            "Never put any part of your body under a vehicle supported only by a jack.",
            "Only lift at the manufacturer's designated jack points.",
            "Re-check lug nut torque after ~50 miles of driving.",
        ],
        "video_query": "how to change a flat car tire step by step",
    },
    ("picture", "frame", "hang", "shelf", "wall mount"): {
        "title": "Hang something on the wall",
        "required_tools": [
            {"name": "Drill", "category": "Power tool", "essential": True},
            {"name": "Screwdriver", "category": "Screwdriver", "essential": True},
            {"name": "Level", "category": "Measuring", "essential": True},
            {"name": "Tape measure", "category": "Measuring", "essential": True},
            {"name": "Wall anchors", "category": "Hardware", "essential": False},
            {"name": "Stud finder", "category": "Measuring", "essential": False},
            {"name": "Pencil", "category": "Other", "essential": False},
        ],
        "steps": [
            "Decide the position and mark the height with a pencil.",
            "Use a stud finder to locate studs, or plan to use wall anchors.",
            "Use the level to mark a straight line and mark drill points.",
            "Drill pilot holes at the marks.",
            "Insert wall anchors if not drilling into a stud.",
            "Drive the screws/hooks, leaving a slight gap if hanging a frame.",
            "Hang the item and check it's level; adjust as needed.",
        ],
        "safety": [
            "Check for hidden electrical wiring or pipes before drilling.",
            "Wear eye protection when drilling.",
        ],
        "video_query": "how to hang a picture frame on the wall straight",
    },
    ("faucet", "tap", "leak", "plumb"): {
        "title": "Fix a leaky faucet",
        "required_tools": [
            {"name": "Adjustable wrench", "category": "Wrench", "essential": True},
            {"name": "Screwdriver", "category": "Screwdriver", "essential": True},
            {"name": "Pliers", "category": "Pliers", "essential": False},
            {"name": "Plumber's tape", "category": "Hardware", "essential": False},
            {"name": "Replacement washers", "category": "Hardware", "essential": False},
        ],
        "steps": [
            "Turn off the water supply under the sink and open the tap to drain it.",
            "Plug the drain so small parts don't fall in.",
            "Remove the handle with a screwdriver and set screws aside.",
            "Unscrew the packing nut with the wrench and pull out the valve stem.",
            "Inspect and replace the worn washer or O-ring.",
            "Reassemble in reverse order, using plumber's tape on threads.",
            "Turn the water back on slowly and check for leaks.",
        ],
        "safety": [
            "Always shut off the water supply before starting.",
            "Don't overtighten fittings — it can crack the fixture.",
        ],
        "video_query": "how to fix a leaky faucet dripping tap",
    },
    ("assemble", "furniture", "flat pack", "ikea"): {
        "title": "Assemble flat-pack furniture",
        "required_tools": [
            {"name": "Screwdriver", "category": "Screwdriver", "essential": True},
            {"name": "Allen key", "category": "Hand tool", "essential": True},
            {"name": "Rubber mallet", "category": "Hammer", "essential": False},
            {"name": "Drill", "category": "Power tool", "essential": False},
        ],
        "steps": [
            "Lay out all parts and hardware and check them against the manual.",
            "Sort screws and fittings into groups by step.",
            "Follow the instructions in order — don't skip ahead.",
            "Keep screws loose until a section is aligned, then tighten.",
            "Attach any backing panels last and check everything is square.",
        ],
        "safety": [
            "Assemble large pieces near their final position.",
            "Get a second person for heavy panels.",
        ],
        "video_query": "how to assemble flat pack furniture tips",
    },
}


def _match_kb(task: str) -> dict | None:
    t = task.lower()
    for keys, plan in KB.items():
        if any(k in t for k in keys):
            return plan
    return None


def _generic_plan(task: str) -> dict:
    clean = task.strip().rstrip("?.!") or "your task"
    return {
        "title": clean[:1].upper() + clean[1:],
        "required_tools": [
            {"name": "Screwdriver", "category": "Screwdriver", "essential": False},
            {"name": "Adjustable wrench", "category": "Wrench", "essential": False},
            {"name": "Pliers", "category": "Pliers", "essential": False},
            {"name": "Tape measure", "category": "Measuring", "essential": False},
            {"name": "Gloves", "category": "Safety", "essential": False},
        ],
        "steps": [
            "Watch the how-to video below to see the full process.",
            "Gather the tools listed and lay out your workspace.",
            "Work carefully step by step, and stop if anything feels unsafe.",
        ],
        "safety": ["Wear appropriate protective gear for the job."],
        "video_query": f"how to {clean}",
    }


def _extract_json_object(text: str) -> dict | None:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        return None
    try:
        data = json.loads(text[start : end + 1])
        return data if isinstance(data, dict) else None
    except json.JSONDecodeError:
        return None


def plan_task(task: str) -> tuple[dict, str]:
    """Return (plan, engine) where engine is 'claude', 'knowledge-base' or 'generic'."""
    if settings.anthropic_api_key:
        try:
            import anthropic

            client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
            msg = client.messages.create(
                model=settings.vision_model,
                max_tokens=1200,
                messages=[{"role": "user", "content": PLAN_PROMPT + task}],
            )
            text = "".join(b.text for b in msg.content if b.type == "text")
            plan = _extract_json_object(text)
            if plan and plan.get("required_tools"):
                plan.setdefault("safety", [])
                plan.setdefault("steps", [])
                plan.setdefault("title", task)
                plan.setdefault("video_query", f"how to {task}")
                return plan, "claude"
        except Exception:
            pass

    kb = _match_kb(task)
    if kb:
        return kb, "knowledge-base"
    return _generic_plan(task), "generic"
