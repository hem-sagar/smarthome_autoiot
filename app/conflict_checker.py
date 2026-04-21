from __future__ import annotations


def check_rule_conflict(rule: dict) -> tuple[bool, str, str]:
    raw = (rule.get("raw_command") or "").lower()
    location = rule.get("location")
    device = rule.get("device")
    action = rule.get("action")
    condition = (rule.get("condition") or "").lower()

    if "ac and heater together" in raw or ("ac" in raw and "heater" in raw):
        return True, "conflict_hallucination", "The command combines AC and heater together, which is conflicting."

    if "turn on" in raw and "turn off" in raw and device:
        return True, "conflict_hallucination", "The command asks for opposite actions in the same request."

    if device == "ac" and action == "turn_on" and "temperature <= 18" in condition:
        return True, "conflict_hallucination", "Cooling on very cold conditions is a conflicting policy."

    if device == "heater" and action == "turn_on" and "temperature >= 28" in condition:
        return True, "conflict_hallucination", "Heating on very hot conditions is a conflicting policy."

    if location == "front_door" and device == "camera" and action in {"lock", "unlock"}:
        return True, "conflict_hallucination", "The selected action conflicts with the device capability."

    return False, "valid", ""
