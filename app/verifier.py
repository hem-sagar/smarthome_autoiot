from __future__ import annotations

import json

from app.config import DEVICE_CATALOG
from app.prompts.templates import VERIFIER_TEMPLATE
from app.providers.gemini_provider import generate_with_gemini


def verify_and_fix_rule(command: str, rule: dict, hallucination_type: str) -> dict:
    llm_result = _verify_with_gemini(command, rule)
    if llm_result:
        repaired_rule = dict(rule)
        repaired_rule.update({
            "location": llm_result.get("location", rule.get("location")),
            "device": llm_result.get("device", rule.get("device")),
            "action": llm_result.get("action", rule.get("action")),
            "condition": llm_result.get("condition", rule.get("condition")),
        })
        return {
            "rule": repaired_rule,
            "fixed": bool(llm_result.get("fixed")),
            "confidence": float(llm_result.get("confidence", 0.55)),
            "explanation": llm_result.get("explanation", ""),
            "hallucination_type": llm_result.get("hallucination_type", hallucination_type),
            "source": "llm_verifier",
        }

    repaired_rule = _heuristic_fix(rule, hallucination_type)
    fixed = repaired_rule != rule
    return {
        "rule": repaired_rule,
        "fixed": fixed,
        "confidence": 0.62 if fixed else 0.3,
        "explanation": _heuristic_explanation(hallucination_type, fixed),
        "hallucination_type": hallucination_type,
        "source": "python_verifier",
    }


def _verify_with_gemini(command: str, rule: dict) -> dict | None:
    prompt = VERIFIER_TEMPLATE.format(
        command=command,
        catalog=json.dumps(DEVICE_CATALOG, indent=2),
        rule_json=json.dumps(rule, indent=2),
    )
    return generate_with_gemini(prompt)


def _heuristic_fix(rule: dict, hallucination_type: str) -> dict:
    fixed = dict(rule)
    raw = (fixed.get("raw_command") or "").lower()

    if hallucination_type == "action_hallucination":
        if fixed.get("device") == "ac":
            fixed["action"] = "turn_on"
        elif fixed.get("device") == "window":
            fixed["action"] = "open"
        elif fixed.get("device") in {"light", "fan", "alarm", "camera"}:
            fixed["action"] = "turn_on"
    elif hallucination_type == "device_hallucination":
        if "toaster" in raw:
            fixed["device"] = "alarm"
            fixed["action"] = "turn_on"
        elif "lock" in raw and fixed.get("location") in {"front_door", "garage", "bedroom"}:
            fixed["device"] = "door_lock"
    elif hallucination_type == "location_hallucination":
        if fixed.get("device") == "light":
            fixed["location"] = "living_room"
        else:
            fixed["location"] = "bedroom"
    elif hallucination_type == "condition_hallucination":
        fixed["condition"] = "occupancy == 1"
    elif hallucination_type == "ambiguous_command":
        if "comfortable" in raw:
            fixed["location"] = fixed.get("location") or "bedroom"
            fixed["device"] = "ac"
            fixed["action"] = "turn_on"
            fixed["condition"] = "temperature >= 27 AND occupancy == 1"
    return fixed


def _heuristic_explanation(hallucination_type: str, fixed: bool) -> str:
    if fixed:
        return f"The verifier replaced unsupported fields for {hallucination_type} with the closest safe supported rule."
    return f"The verifier could not safely repair the {hallucination_type}."
