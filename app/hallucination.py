from __future__ import annotations
from app.config import DEVICE_CATALOG, CONFIDENCE_THRESHOLD

def classify_rule(rule: dict) -> tuple[str, float, str]:
    location = rule.get("location")
    device = rule.get("device")
    action = rule.get("action")
    condition = rule.get("condition") or ""
    raw = (rule.get("raw_command") or "").lower()

    if not location or location not in DEVICE_CATALOG:
        return "location_hallucination", 0.25, "Unknown or unsupported location"
    if not device or device not in DEVICE_CATALOG[location]:
        return "device_hallucination", 0.20, "Unknown or unsupported device for that location"
    if not action or action not in DEVICE_CATALOG[location][device]:
        return "action_hallucination", 0.20, "Unsupported action for selected device"
    if "bathroom" in raw:
        return "location_hallucination", 0.18, "Bathroom is not part of the supported dataset"
    if "when" in raw and condition.strip() == "occupancy == 1":
        return "condition_hallucination", 0.45, "The condition was underspecified and defaulted to occupancy"
    if "comfortable" in raw:
        return "ambiguous_command", 0.58, "Comfort command is abstract and may require clarification"
    return "valid", 0.90, ""

def should_mark_uncertain(confidence: float) -> bool:
    return confidence < CONFIDENCE_THRESHOLD
