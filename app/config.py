from __future__ import annotations
import os
from dotenv import load_dotenv

load_dotenv()

DEVICE_CATALOG = {
    "living_room": {
        "light": ["turn_on", "turn_off"],
        "fan": ["turn_on", "turn_off"],
        "ac": ["turn_on", "turn_off", "set_temperature"],
        "heater": ["turn_on", "turn_off", "set_temperature"],
        "window": ["open", "close"],
    },
    "bedroom": {
        "light": ["turn_on", "turn_off"],
        "fan": ["turn_on", "turn_off"],
        "ac": ["turn_on", "turn_off", "set_temperature"],
        "heater": ["turn_on", "turn_off", "set_temperature"],
        "door_lock": ["lock", "unlock"],
    },
    "kitchen": {
        "light": ["turn_on", "turn_off"],
        "fan": ["turn_on", "turn_off"],
        "alarm": ["turn_on", "turn_off"],
        "window": ["open", "close"],
    },
    "garage": {
        "light": ["turn_on", "turn_off"],
        "door_lock": ["lock", "unlock"],
        "fan": ["turn_on", "turn_off"],
        "alarm": ["turn_on", "turn_off"],
    },
    "front_door": {
        "door_lock": ["lock", "unlock"],
        "alarm": ["turn_on", "turn_off"],
        "camera": ["turn_on", "turn_off"],
        "light": ["turn_on", "turn_off"],
    },
}

ROOMS = list(DEVICE_CATALOG.keys())
WEATHER_STATES = ["sunny", "rainy", "cloudy", "windy"]
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.60"))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
USE_GEMINI = os.getenv("USE_GEMINI", "false").lower() == "true"
