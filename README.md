# AutoIoT Chat UI Upgrade

## Run
```bash
pip install -r requirements.txt
mkdir data outputs
python -m app.data_generator
python run_pipeline.py --mode zero_shot
python run_pipeline.py --mode one_shot
python -m streamlit run dashboard.py
```

## Pipeline
```text
User Chat
  -> LLM 1 Generator
  -> JSON Rule
  -> Python Validator
  -> LLM 2 Verifier/Fixer
  -> Python Conflict Checker
  -> LLM 3 Resolver/Explainer
  -> Simulator Execution
  -> Chat UI Response
```

## What this adds
- chat-style command input
- fixed pipeline-driven generator flow in the UI
- rule parsing result
- hallucination type taxonomy
- verifier and resolver stages
- confidence score
- uncertainty warning
- optional "add valid rule to simulation"
- dashboard tables and charts

## Notes
- The chat UI only asks the user for natural-language commands. Prompt strategy controls are not exposed in the UI.
- The generated dataset includes valid commands and labeled hallucination cases.
- See `docs/hallucination_notes.md` for the project taxonomy summary.
