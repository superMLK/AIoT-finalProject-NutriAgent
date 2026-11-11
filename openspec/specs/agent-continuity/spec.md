# Capability Spec: Agent Continuity & Optimization Harness
Capability Path: `openspec/specs/agent-continuity/spec.md`

## Overview
Defines machine-verifiable requirements for AI agent onboarding, automated regression testing, objective benchmarking, and path-resilient execution.

---

### Requirement: Machine-Readable Benchmark Output
The system SHALL provide an automated benchmark harness capable of evaluating the entire agent pipeline and emitting structured JSON formatted metrics.

#### Scenario: Agent Benchmark Execution
- **GIVEN** an AI agent testing code modifications
- **WHEN** `python benchmark.py` is invoked
- **THEN** the process SHALL exit with code 0
- **AND** standard output SHALL contain `[AGENT_JSON_OUTPUT_START]` and `[AGENT_JSON_OUTPUT_END]`
- **AND** the enclosed JSON SHALL contain `clinical_violation_rate_pct`, `caloric_mae_kcal`, and `mean_latency_ms`

---

### Requirement: Cross-Machine Path Resilience
All file loading mechanisms SHALL resolve paths dynamically relative to `Path(__file__)` and SHALL NOT rely on hardcoded absolute filesystem paths.

#### Scenario: Execution from arbitrary working directories
- **GIVEN** a terminal located in an arbitrary subfolder (e.g. `tests/` or parent directory)
- **WHEN** the agent or test runner loads `data/meal_catalog.json` or `data/sample_health_reports.json`
- **THEN** the files SHALL be loaded successfully without raising `FileNotFoundError`

---

### Requirement: Clinical & Allergen Zero-Regression Guardrail
Any agent optimization SHALL maintain a Clinical Violation Rate (CVR) and Allergen Violation Rate (AVR) of exactly $0.0\%$.

#### Scenario: Verification during agent refactoring
- **GIVEN** an optimized DRL or LBS algorithm implemented by an AI agent
- **WHEN** unit tests in `tests/test_agent.py` and `benchmark.py` are executed
- **THEN** all tests SHALL pass
- **AND** `benchmark_status` in the JSON benchmark report SHALL be `"PASSED"`
