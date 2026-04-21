# AutoIoT Hallucination Notes

This project follows a staged pipeline for smart-home command handling:

1. User chat input
2. LLM 1 generator
3. JSON rule
4. Python validator and hallucination typing
5. LLM 2 verifier/fixer
6. Python conflict checker
7. LLM 3 resolver/explainer
8. Simulator execution
9. Chat UI response

The dataset now includes these issue types:

- `location_hallucination`
- `device_hallucination`
- `action_hallucination`
- `condition_hallucination`
- `conflict_hallucination`
- `ambiguous_command`

Confidence is conservative by design:

- parser confidence is only one signal
- validation and conflict checks can lower confidence
- unresolved issues are marked `uncertain`
