from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta
import random
from pathlib import Path
import pandas as pd
from app.config import ROOMS, WEATHER_STATES

@dataclass
class GeneratorConfig:
    start_time: datetime = datetime(2026, 4, 1, 0, 0, 0)
    periods: int = 120
    step_minutes: int = 30
    seed: int = 42

VALID_COMMANDS = [
    "Turn on living room light when motion is detected at night",
    "Keep bedroom comfortable",
    "Lock front door at night",
    "Turn on garage fan when humidity is high",
    "Turn off living room light in the morning",
]
INVALID_COMMANDS = [
    {"command": "Open AC in bedroom", "hallucination_type": "action_hallucination"},
    {"command": "Turn on toaster in garage", "hallucination_type": "device_hallucination"},
    {"command": "Unlock camera at front door", "hallucination_type": "action_hallucination"},
    {"command": "Turn on AC and heater together in living room", "hallucination_type": "conflict_hallucination"},
    {"command": "Turn on light in bathroom when motion is detected", "hallucination_type": "location_hallucination"},
    {"command": "Keep the house comfortable", "hallucination_type": "ambiguous_command"},
    {"command": "Turn on bedroom heater when it feels nice", "hallucination_type": "condition_hallucination"},
]

def _time_bucket(hour: int) -> str:
    if 5 <= hour < 12:
        return "morning"
    if 12 <= hour < 17:
        return "afternoon"
    if 17 <= hour < 21:
        return "evening"
    return "night"

def generate_sensor_data(config: GeneratorConfig) -> pd.DataFrame:
    random.seed(config.seed)
    rows = []
    current = config.start_time
    for _ in range(config.periods):
        for room in ROOMS:
            hour = current.hour
            time_bucket = _time_bucket(hour)
            occupancy = 1 if random.random() < (0.7 if time_bucket in {"evening", "night"} else 0.45) else 0
            motion = 1 if random.random() < (0.55 if occupancy else 0.15) else 0
            base_temp = 18 + (8 if time_bucket == "afternoon" else 3 if time_bucket == "evening" else 0)
            temperature = base_temp + random.randint(-2, 7)
            humidity = random.randint(30, 85)
            light_level = random.randint(5, 45) if time_bucket == "night" else random.randint(30, 100)
            weather = random.choice(WEATHER_STATES)
            rows.append({
                "timestamp": current.isoformat(),
                "room": room,
                "time_bucket": time_bucket,
                "temperature": temperature,
                "humidity": humidity,
                "light_level": light_level,
                "motion": motion,
                "occupancy": occupancy,
                "weather": weather,
            })
        current += timedelta(minutes=config.step_minutes)
    return pd.DataFrame(rows)

def generate_user_commands(seed: int = 42, total: int = 40) -> pd.DataFrame:
    random.seed(seed)
    rows = []
    for idx in range(total):
        if random.random() < 0.5:
            cmd = random.choice(VALID_COMMANDS)
            expected_hallucination = False
            expected_type = "valid"
        else:
            invalid = random.choice(INVALID_COMMANDS)
            cmd = invalid["command"]
            expected_hallucination = True
            expected_type = invalid["hallucination_type"]
        rows.append({
            "command_id": f"CMD-{idx+1:03d}",
            "user_command": cmd,
            "expected_hallucination": expected_hallucination,
            "expected_type": expected_type,
        })
    return pd.DataFrame(rows)

def save_default_datasets(sensor_path: str, command_path: str):
    Path(sensor_path).parent.mkdir(parents=True, exist_ok=True)
    Path(command_path).parent.mkdir(parents=True, exist_ok=True)
    sensor_df = generate_sensor_data(GeneratorConfig())
    command_df = generate_user_commands()
    sensor_df.to_csv(sensor_path, index=False)
    command_df.to_csv(command_path, index=False)
    return sensor_df, command_df

if __name__ == "__main__":
    save_default_datasets("data/sensor_data.csv", "data/commands.csv")
    print("Saved datasets.")
