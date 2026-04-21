from __future__ import annotations
import json
from app.config import DEVICE_CATALOG
from app.prompts.templates import ZERO_SHOT_TEMPLATE, ONE_SHOT_TEMPLATE
from app.providers.gemini_provider import generate_with_gemini, get_last_gemini_error
from app.rule_engine import RuleEngine

def parse_command(command: str, mode: str = "zero_shot") -> dict:
    template = ZERO_SHOT_TEMPLATE if mode == "zero_shot" else ONE_SHOT_TEMPLATE
    prompt = template.format(command=command, catalog=json.dumps(DEVICE_CATALOG, indent=2))

    parsed = generate_with_gemini(prompt)
    if parsed:
        return {
            "rule_id": "GEMINI",
            "source": "gemini",
            "raw_command": command,
            "location": parsed.get("location"),
            "device": parsed.get("device"),
            "action": parsed.get("action"),
            "condition": parsed.get("condition", "occupancy == 1"),
            "priority": 5,
            "enabled": True,
            "description": command,
            "llm_confidence": parsed.get("confidence", 0.5),
            "uncertain_reason": parsed.get("uncertain_reason", ""),
            "gemini_error": "",
        }

    fallback_rule = RuleEngine().parse_command(command)
    fallback_rule["gemini_error"] = get_last_gemini_error()
    return fallback_rule
