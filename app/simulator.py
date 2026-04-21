from __future__ import annotations
import pandas as pd

def simulate(sensor_df: pd.DataFrame, rules: list[dict]) -> pd.DataFrame:
    actions = []
    for _, row in sensor_df.iterrows():
        for rule in rules:
            if not rule.get("enabled", True):
                continue
            if rule.get("location") != row["room"]:
                continue
            cond = rule.get("condition", "")
            if "motion == 1" in cond and int(row["motion"]) != 1:
                continue
            if "time_bucket == 'night'" in cond and row["time_bucket"] != "night":
                continue
            if "time_bucket == 'morning'" in cond and row["time_bucket"] != "morning":
                continue
            if "humidity >= 70" in cond and float(row["humidity"]) < 70:
                continue
            if "temperature >= 27" in cond and float(row["temperature"]) < 27:
                continue
            if "temperature >= 28" in cond and float(row["temperature"]) < 28:
                continue
            if "temperature <= 18" in cond and float(row["temperature"]) > 18:
                continue
            actions.append({
                "timestamp": row["timestamp"],
                "room": row["room"],
                "rule_id": rule["rule_id"],
                "device": rule["device"],
                "action": rule["action"],
                "condition": cond,
            })
    return pd.DataFrame(actions)
