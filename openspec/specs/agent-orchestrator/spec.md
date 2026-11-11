# Capability: Agent Orchestration, Conversational Dialogue & Grounded Decision Synthesis
Capability Path: `openspec/specs/agent-orchestrator/spec.md`

## Overview
Unites the 8-stage Domain AI Agent pipeline, supports multi-turn ChatGPT-style natural language conversation (`chat()`), enforces never-relax empty pool safety, and verifies numerical consistency (`numbers_in(E) == db_values(R)`).

---

### Requirement: 8-Stage Domain Agent Execution Pipeline
The agent SHALL execute the sequential pipeline: Scenario $\rightarrow$ IoT Ingestion & Plausibility Check $\rightarrow$ Dynamic TDEE Planning $\rightarrow$ Spatial LBS Retrieval $\rightarrow$ Clinical & TFDA-11 Allergen Hard Pruning $\rightarrow$ Gemini Contextual Ranking $\rightarrow$ Grounded Explanation Verification $\rightarrow$ Conversational Interaction.

#### Scenario: End-to-end execution
- **GIVEN** a user profile, location, and meal type
- **WHEN** `run_recommendation()` or `chat()` is invoked
- **THEN** the system SHALL return Top-3 ranked recommendations when `SafePool` is non-empty
- **AND** when `SafePool` is empty, the system SHALL NOT relax clinical or allergen rules and SHALL return `status == "no_compliant_meal"` with `order_tips`

---

### Requirement: Numerical Consistency Verification
The system SHALL verify that all nutritional numbers cited in explanations match the database fields (`assert numbers_in(E) == db_values(R)`).

#### Scenario: Explanation consistency check
- **GIVEN** a recommended meal from `meal_catalog.json`
- **WHEN** `_generate_clinical_explanation()` produces the rationale
- **THEN** `verify_explanation_consistency()` SHALL return `True`
