from __future__ import annotations
from pathlib import Path
import json
import pandas as pd
from app.data_generator import save_default_datasets
from app.chat_service import analyze_command
from app.simulator import simulate

def run_pipeline(mode: str = "zero_shot") -> None:
    Path("outputs").mkdir(exist_ok=True)
    sensor_path = "data/sensor_data.csv"
    command_path = "data/commands.csv"

    if not Path(sensor_path).exists() or not Path(command_path).exists():
        save_default_datasets(sensor_path, command_path)

    sensor_df = pd.read_csv(sensor_path)
    command_df = pd.read_csv(command_path)

    records = []
    final_rules = []

    for _, row in command_df.iterrows():
        analysis = analyze_command(row["user_command"], mode=mode)
        for item in analysis["results"]:
            rule = item["rule"]
            records.append({
                "command_id": row["command_id"],
                "user_command": row["user_command"],
                "rule_id": rule.get("rule_id"),
                "location": rule.get("location"),
                "device": rule.get("device"),
                "action": rule.get("action"),
                "condition": rule.get("condition"),
                "hallucination_type": item["hallucination_type"],
                "confidence": item["confidence"],
                "uncertain": item["uncertain"],
                "reason": item["reason"],
                "resolved": item["resolved"],
                "verifier_note": item["verifier_note"],
                "resolver_note": item["resolver_note"],
                "pipeline_trace": " -> ".join(item["pipeline_trace"]),
                "prompt_mode": item["prompt_mode"],
                "gemini_error": item["gemini_error"],
            })
            if item["hallucination_type"] == "valid":
                final_rules.append(rule)

    results_df = pd.DataFrame(records)
    results_df.to_csv("outputs/command_results.csv", index=False)

    sim_df = simulate(sensor_df, final_rules)
    sim_df.to_csv("outputs/simulation_actions.csv", index=False)

    summary = {
        "total_commands": int(len(results_df)),
        "valid_rules": int((results_df["hallucination_type"] == "valid").sum()),
        "hallucinations": int((results_df["hallucination_type"] != "valid").sum()),
        "uncertain": int(results_df["uncertain"].sum()),
        "mode": mode,
    }
    Path("outputs/summary.json").write_text(json.dumps(summary, indent=2))
    print("Pipeline finished. Check outputs/")
