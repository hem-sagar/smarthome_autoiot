from __future__ import annotations

import json

from app.prompts.templates import RESOLVER_TEMPLATE
from app.providers.gemini_provider import generate_with_gemini


def resolve_remaining_issue(command: str, rule: dict, issue: str) -> dict:
    llm_result = _resolve_with_gemini(command, rule, issue)
    if llm_result:
        return {
            "explanation": llm_result.get("explanation", issue),
            "safe_resolution": llm_result.get("safe_resolution", ""),
            "confidence": float(llm_result.get("confidence", 0.45)),
            "uncertain_reason": llm_result.get("uncertain_reason", ""),
            "source": "llm_resolver",
        }

    return {
        "explanation": issue,
        "safe_resolution": _fallback_resolution(rule),
        "confidence": 0.35,
        "uncertain_reason": "The system could not fully resolve the issue with high confidence.",
        "source": "python_resolver",
    }


def _resolve_with_gemini(command: str, rule: dict, issue: str) -> dict | None:
    prompt = RESOLVER_TEMPLATE.format(
        command=command,
        rule_json=json.dumps(rule, indent=2),
        issue=issue,
    )
    return generate_with_gemini(prompt)


def _fallback_resolution(rule: dict) -> str:
    device = rule.get("device") or "device"
    location = rule.get("location") or "selected location"
    return f"Please rephrase the command for the {device} in {location} using a single supported action and a clear condition."
