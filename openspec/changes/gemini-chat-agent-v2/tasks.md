# Implementation Tasks: `gemini-chat-agent-v2`

- [x] 1. Run baseline benchmark (`python benchmark.py`) and inspect current metrics.
- [x] 2. Update `src/clinical_rules.py` to support TFDA 11 allergen taxonomy, CKD rule, and `generate_order_tips()`.
- [x] 3. Update `src/iot_pipeline.py` to add `plausibility_check()`, `low_confidence` fallback flag, and 900 kcal single-meal budget cap.
- [x] 4. Replace PyTorch DQN in `src/recommender.py` with `GeminiRecommender` (connecting to Gemini API for preference scoring, intent extraction, and grounded response generation, while keeping online preference weight adaptation).
- [x] 5. Update `src/agent.py` to remove unsafe fallback relaxation, enforce numerical consistency check, and add multi-turn `chat()` conversational orchestration.
- [x] 6. Redesign `app.py` into a ChatGPT-style conversational Agent UI with chat stream, reasoning trace, embedded Top-3 meal cards, and sidebar controls (including Gemini API Key input).
- [x] 7. Update `PROPOSAL.md`, `DESIGN.md`, `requirements.txt`, and `tests/test_agent.py`.
- [x] 8. Run unit tests (`python -m unittest tests/test_agent.py`) and benchmark (`python benchmark.py`) to verify 0.0% CVR/AVR and full compliance.
