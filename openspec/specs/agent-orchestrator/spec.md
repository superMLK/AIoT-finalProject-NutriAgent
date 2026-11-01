# Capability: Agent Orchestration & Explainable Decision Synthesis
Capability Path: `openspec/specs/agent-orchestrator/spec.md`

## Overview
Unites the 8-stage Domain AI Agent pipeline and synthesizes transparent clinical and metabolic explanations for each recommendation.

---

### Requirement: 8-Stage Domain Agent Execution Pipeline
The agent SHALL execute the sequential pipeline: Scenario $\rightarrow$ Ingestion $\rightarrow$ Planning $\rightarrow$ Retrieval $\rightarrow$ Clinical Pruning $\rightarrow$ DRL Ranking $\rightarrow$ Decision $\rightarrow$ Interaction.

#### Scenario: End-to-end execution
- **GIVEN** a user profile, location, and meal type
- **WHEN** `run_recommendation()` is invoked
- **THEN** the system SHALL return Top-3 ranked recommendations
- **AND** each recommendation SHALL include meal details, nutritional facts, distance, and clinical explanation

---

### Requirement: Clinically Grounded Rationales
The system SHALL generate an explanation for each recommended meal explicitly mentioning the user's specific health indicators and Google Fit activity telemetry.

#### Scenario: Explanation contents
- **GIVEN** a recommended meal for a hypertensive user with 6,800 steps
- **WHEN** explanations are generated
- **THEN** the explanation text SHALL explicitly state sodium compliance ($< 700\,\text{mg}$)
- **AND** the explanation text SHALL reference the user's physical steps or metabolic target
