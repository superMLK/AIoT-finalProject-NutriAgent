# OpenSpec Tasks: Agent Continuity & Optimization Harness
Change ID: `agentic-continuity-optimization`

## Implementation Checklist
- [x] 1. Agent Directives & Protocol Setup
  - [x] 1.1 Create universal `AGENTS.md` specifying OpenSpec development rules, architecture, and invariants.
  - [x] 1.2 Document 4 prioritized optimization tracks for future AI agents (Dueling DQN, CGM simulation, semantic embeddings, multi-agent tools).
- [x] 2. Automated Benchmark Harness
  - [x] 2.1 Implement `benchmark.py` evaluating CVR, AVR, caloric MAE, and latency across 5 patient profiles and 3 activity scenarios.
  - [x] 2.2 Add machine-readable `[AGENT_JSON_OUTPUT_START]` output format for automated agent ingestion.
  - [x] 2.3 Verify `benchmark.py` executes in under 2 seconds with PASSED status.
- [x] 3. Path Resilience Refactoring
  - [x] 3.1 Refactor `src/spatial_lbs.py` to use `Path(__file__).resolve().parent.parent`.
  - [x] 3.2 Refactor `src/agent.py` to allow optional catalog paths with dynamic defaults.
  - [x] 3.3 Refactor `app.py`, `demo_run.py`, and `tests/test_agent.py` to resolve datasets via `Path`.
- [x] 4. One-Click Cross-Platform Runners
  - [x] 4.1 Author `setup_env.bat` and `setup_env.sh`.
  - [x] 4.2 Author `run_demo.bat` and `run_demo.sh`.
  - [x] 4.3 Author `run_web.bat` and `run_web.sh`.
  - [x] 4.4 Author `run_test.bat` and `run_test.sh`.
- [x] 5. Human Handover Guide
  - [x] 5.1 Author `HANDOVER.md` outlining zero-friction onboarding in 3 steps, codebase map, and developer extension scenarios.
