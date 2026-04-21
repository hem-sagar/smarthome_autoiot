from __future__ import annotations
from app.llm_parser import parse_command
from app.hallucination import classify_rule, should_mark_uncertain
from app.verifier import verify_and_fix_rule
from app.conflict_checker import check_rule_conflict
from app.resolver import resolve_remaining_issue
from app.rule_engine import RuleEngine

def analyze_command(command: str, mode: str = "zero_shot") -> dict:
    rule = parse_command(command, mode=mode)
    expanded = RuleEngine().expand_rule(rule)

    analyzed = []
    for item in expanded:
        original_type, confidence, reason = classify_rule(item)
        hall_type = original_type
        working_rule = dict(item)
        pipeline_trace = ["generator", "validator"]
        verifier_note = ""
        resolver_note = ""

        if working_rule.get("source") == "gemini" and working_rule.get("llm_confidence") is not None:
            try:
                confidence = min(float(working_rule["llm_confidence"]), confidence)
            except Exception:
                pass

        if hall_type != "valid":
            pipeline_trace.append("verifier")
            verifier_result = verify_and_fix_rule(command, working_rule, hall_type)
            verifier_note = verifier_result["explanation"]
            working_rule = verifier_result["rule"]
            fixed_type, fixed_conf, fixed_reason = classify_rule(working_rule)
            if verifier_result["fixed"]:
                confidence = max(min(confidence, fixed_conf), verifier_result["confidence"])
            else:
                confidence = min(confidence, verifier_result["confidence"])
            if verifier_result["fixed"] and fixed_type == "valid":
                hall_type = "valid"
                reason = fixed_reason
            else:
                hall_type = fixed_type
                reason = fixed_reason or reason

        pipeline_trace.append("conflict_checker")
        has_conflict, conflict_type, conflict_reason = check_rule_conflict(working_rule)
        if has_conflict:
            hall_type = conflict_type
            reason = conflict_reason
            confidence = min(confidence, 0.25)

        if hall_type != "valid":
            pipeline_trace.append("resolver")
            resolution = resolve_remaining_issue(command, working_rule, reason)
            resolver_note = resolution["safe_resolution"]
            confidence = min(confidence, resolution["confidence"])
            if resolution["uncertain_reason"]:
                reason = f"{reason} {resolution['uncertain_reason']}".strip()

        uncertain = should_mark_uncertain(confidence) or hall_type != "valid"
        resolved = "resolved" if original_type != "valid" and hall_type == "valid" else ""

        analyzed.append({
            "rule": working_rule,
            "hallucination_type": hall_type,
            "confidence": round(float(confidence), 2),
            "uncertain": uncertain,
            "reason": reason,
            "resolved": resolved,
            "verifier_note": verifier_note,
            "resolver_note": resolver_note,
            "pipeline_trace": pipeline_trace,
            "prompt_mode": mode,
            "gemini_error": working_rule.get("gemini_error", ""),
        })
    return {"command": command, "results": analyzed}
