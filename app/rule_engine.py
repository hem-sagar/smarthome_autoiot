from __future__ import annotations
import re, uuid
from typing import Dict, List
from app.config import DEVICE_CATALOG, ROOMS

DEVICE_ALIASES = {
    "light": "light", "lights": "light",
    "fan": "fan",
    "ac": "ac", "air conditioner": "ac",
    "heater": "heater",
    "window": "window",
    "lock": "door_lock", "door": "door_lock", "door lock": "door_lock",
    "alarm": "alarm",
    "camera": "camera",
}

ACTION_ALIASES = {
    "turn on": "turn_on", "switch on": "turn_on",
    "turn off": "turn_off", "switch off": "turn_off",
    "open": "open", "close": "close",
    "lock": "lock", "unlock": "unlock",
    "keep comfortable": "auto_comfort", "ac on": "turn_on"
}

class RuleEngine:
    def parse_command(self, command: str) -> Dict:
        text = command.strip().lower()
        location = self._extract_location(text)
        device = self._extract_device(text)
        action = self._extract_action(text)
        conditions = self._extract_conditions(text)

        structured = {
            "rule_id": f"LLM-{uuid.uuid4().hex[:8].upper()}",
            "source": "local_parser",
            "raw_command": command,
            "location": location,
            "device": device,
            "action": action,
            "condition": self._conditions_to_expression(conditions),
            "priority": 5,
            "enabled": True,
            "description": command,
        }

        if action == "auto_comfort":
            structured["location"] = location or "bedroom"
            structured["device"] = "ac"
            structured["action"] = "turn_on"
            structured["condition"] = "temperature >= 27 AND occupancy == 1"
            structured["secondary_rule"] = {
                "location": location or "bedroom",
                "device": "heater",
                "action": "turn_on",
                "condition": "temperature <= 18 AND occupancy == 1",
            }
        return structured

    def _extract_location(self, text: str) -> str | None:
        for room in ROOMS:
            phrase = room.replace("_", " ")
            if phrase in text:
                return room
        if "front door" in text:
            return "front_door"
        return None

    def _extract_device(self, text: str) -> str | None:
        for alias, canonical in sorted(DEVICE_ALIASES.items(), key=lambda x: len(x[0]), reverse=True):
            if alias in text:
                return canonical
        if "comfortable" in text:
            return "comfort_controller"
        match = re.search(r"turn on ([a-z ]+?) in", text)
        if match:
            return match.group(1).strip().replace(" ", "_")
        return None

    def _extract_action(self, text: str) -> str | None:
        for alias, canonical in sorted(ACTION_ALIASES.items(), key=lambda x: len(x[0]), reverse=True):
            if alias in text:
                return canonical
        if "comfortable" in text:
            return "auto_comfort"
        return None

    def _extract_conditions(self, text: str) -> List[str]:
        conditions = []
        if "motion" in text:
            conditions.append("motion == 1")
        if "night" in text:
            conditions.append("time_bucket == 'night'")
        if "morning" in text:
            conditions.append("time_bucket == 'morning'")
        if "humidity is high" in text or "high humidity" in text:
            conditions.append("humidity >= 70")
        if "hot" in text:
            conditions.append("temperature >= 28")
        if "cold" in text:
            conditions.append("temperature <= 18")
        if not conditions:
            conditions.append("occupancy == 1")
        return conditions

    def _conditions_to_expression(self, conditions: List[str]) -> str:
        return " AND ".join(conditions)

    def expand_rule(self, rule: Dict) -> List[Dict]:
        rules = [rule]
        secondary = rule.get("secondary_rule")
        if secondary:
            rules.append({
                "rule_id": f"{rule['rule_id']}-B",
                "source": rule["source"],
                "raw_command": rule["raw_command"],
                "location": secondary["location"],
                "device": secondary["device"],
                "action": secondary["action"],
                "condition": secondary["condition"],
                "priority": 5,
                "enabled": True,
                "description": f"Secondary comfort rule for: {rule['raw_command']}",
            })
        return rules
