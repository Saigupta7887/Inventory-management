"""Vision service: turn a photo of a location into a list of detected tools.

If ANTHROPIC_API_KEY is configured, this calls Claude with the image and asks
for a structured list of tools. Otherwise it returns a deterministic MOCK
result so the whole photo -> detection -> confirm -> item flow works end to end
without any credentials. Detections are always reviewed by the user before
becoming inventory (human-in-the-loop).
"""

import base64
import json

from .config import get_settings

settings = get_settings()

DETECTION_PROMPT = (
    "You are a tool-inventory assistant. Look at this photo of a storage "
    "location (a desk, drawer, shelf, pegboard, toolbox, etc.) and identify "
    "every distinct tool or piece of equipment you can see.\n\n"
    "Return ONLY a JSON array. Each element must be an object with keys:\n"
    '  "label": short human name of the tool (e.g. "Phillips screwdriver"),\n'
    '  "category": a broad category (e.g. "Screwdriver", "Power tool", '
    '"Wrench", "Measuring", "Hand tool", "Hardware"),\n'
    '  "confidence": a number from 0 to 1,\n'
    '  "bbox": {"x":..,"y":..,"w":..,"h":..} normalized 0..1 for the tool\'s '
    "location in the image.\n"
    "Do not include any prose outside the JSON array."
)

MOCK_DETECTIONS = [
    {"label": "Claw hammer", "category": "Hand tool", "confidence": 0.94,
     "bbox": {"x": 0.08, "y": 0.15, "w": 0.20, "h": 0.35}},
    {"label": "Phillips screwdriver", "category": "Screwdriver", "confidence": 0.88,
     "bbox": {"x": 0.34, "y": 0.20, "w": 0.10, "h": 0.30}},
    {"label": "Adjustable wrench", "category": "Wrench", "confidence": 0.83,
     "bbox": {"x": 0.50, "y": 0.25, "w": 0.18, "h": 0.28}},
    {"label": "Tape measure", "category": "Measuring", "confidence": 0.79,
     "bbox": {"x": 0.72, "y": 0.30, "w": 0.16, "h": 0.20}},
    {"label": "Cordless drill", "category": "Power tool", "confidence": 0.76,
     "bbox": {"x": 0.20, "y": 0.55, "w": 0.30, "h": 0.35}},
]


def _extract_json_array(text: str) -> list[dict]:
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1 or end < start:
        return []
    try:
        data = json.loads(text[start : end + 1])
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []


def detect_tools(image_bytes: bytes, content_type: str = "image/jpeg") -> tuple[list[dict], str]:
    """Return (detections, engine) where engine is 'claude' or 'mock'."""
    if not settings.anthropic_api_key:
        return MOCK_DETECTIONS, "mock"

    try:
        import anthropic

        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        b64 = base64.standard_b64encode(image_bytes).decode("utf-8")
        media_type = content_type if content_type.startswith("image/") else "image/jpeg"
        message = client.messages.create(
            model=settings.vision_model,
            max_tokens=1500,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": DETECTION_PROMPT},
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": b64,
                            },
                        },
                    ],
                }
            ],
        )
        text = "".join(block.text for block in message.content if block.type == "text")
        detections = _extract_json_array(text)
        if not detections:
            return MOCK_DETECTIONS, "mock"
        return detections, "claude"
    except Exception:
        # Any failure (network, quota, parsing) falls back to the mock so the
        # prototype never breaks the flow.
        return MOCK_DETECTIONS, "mock"
