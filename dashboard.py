import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from app.chat_service import analyze_command
from app.data_generator import save_default_datasets
from app.simulator import simulate

st.set_page_config(page_title="AutoIoT Chat Dashboard", layout="wide")

# Ensure folders and datasets exist
Path("data").mkdir(exist_ok=True)
Path("outputs").mkdir(exist_ok=True)
if not Path("data/sensor_data.csv").exists() or not Path("data/commands.csv").exists():
    save_default_datasets("data/sensor_data.csv", "data/commands.csv")

st.title("AutoIoT Chat UI + Dashboard")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "ad_hoc_rules" not in st.session_state:
    st.session_state.ad_hoc_rules = []

left, right = st.columns([1.1, 1.2])

with left:
    st.subheader("Smart Home Chat")
    user_input = st.chat_input("Type a smart-home command...")

    if user_input:
        analysis = analyze_command(user_input)
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input,
        })

        for item in analysis["results"]:
            rule = item["rule"]
            status = "Valid rule" if item["hallucination_type"] == "valid" else f"Issue: {item['hallucination_type']}"
            uncertain_text = "Uncertain" if item["uncertain"] else "Confident"
            reply = (
                f"{status}\n\n"
                f"Pipeline: {' -> '.join(item['pipeline_trace'])}\n"
                f"Location: {rule.get('location')}\n"
                f"Device: {rule.get('device')}\n"
                f"Action: {rule.get('action')}\n"
                f"Condition: {rule.get('condition')}\n"
                f"Confidence: {item['confidence']} ({uncertain_text})\n"
                f"Reason: {item['reason'] or 'No issue'}\n"
                f"Gemini: {item['gemini_error'] or rule.get('source', 'unknown')}\n"
                f"Verifier: {item['verifier_note'] or 'No verifier change needed'}\n"
                f"Resolver: {item['resolver_note'] or item['resolved'] or 'No resolver change needed'}"
            )
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": reply,
                "rule": rule,
                "is_valid": item["hallucination_type"] == "valid",
            })

    for idx, msg in enumerate(st.session_state.chat_history):
        with st.chat_message("user" if msg["role"] == "user" else "assistant"):
            st.markdown(msg["content"])
            if msg["role"] == "assistant" and msg.get("is_valid"):
                if st.button(f"Add this rule to simulation #{idx}", key=f"add_rule_{idx}"):
                    st.session_state.ad_hoc_rules.append(msg["rule"])
                    st.success("Rule added to simulation set.")

    if st.button("Clear chat history"):
        st.session_state.chat_history = []
        st.session_state.ad_hoc_rules = []
        st.rerun()

with right:
    st.subheader("Dashboard")

    summary_path = Path("outputs/summary.json")
    results_path = Path("outputs/command_results.csv")

    if summary_path.exists() and results_path.exists():
        summary = json.loads(summary_path.read_text())
        results = pd.read_csv(results_path)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Commands", summary["total_commands"])
        c2.metric("Valid rules", summary["valid_rules"])
        c3.metric("Hallucinations", summary["hallucinations"])
        c4.metric("Uncertain", summary["uncertain"])

        st.subheader("Batch Command Results")
        st.dataframe(results, use_container_width=True)

        if not results.empty:
            counts = results["hallucination_type"].fillna("valid").value_counts()
            fig, ax = plt.subplots(figsize=(7, 3.5))
            counts.plot(kind="bar", ax=ax)
            ax.set_ylabel("Count")
            ax.set_title("Hallucination Types")
            st.pyplot(fig)

            fig2, ax2 = plt.subplots(figsize=(7, 3.5))
            results["confidence"].astype(float).plot(kind="hist", bins=10, ax=ax2)
            ax2.set_xlabel("Confidence")
            ax2.set_title("Confidence Distribution")
            st.pyplot(fig2)

    st.subheader("Ad-hoc Simulation")
    if st.session_state.ad_hoc_rules:
        st.write(f"Rules added from chat: {len(st.session_state.ad_hoc_rules)}")
        if st.button("Run simulation with chat-added rules"):
            sensor_df = pd.read_csv("data/sensor_data.csv")
            sim_df = simulate(sensor_df, st.session_state.ad_hoc_rules)
            sim_df.to_csv("outputs/chat_simulation_actions.csv", index=False)
            st.success("Chat simulation completed.")
            st.dataframe(sim_df, use_container_width=True)
    else:
        st.info("Add valid rules from the chat to run ad-hoc simulation.")

    st.subheader("Commands")
    st.code("python run_pipeline.py --mode zero_shot\npython -m streamlit run dashboard.py", language="bash")
