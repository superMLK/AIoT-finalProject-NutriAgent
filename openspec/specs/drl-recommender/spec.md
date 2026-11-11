# Capability: Gemini API Contextual Recommender & Online Preference Adaptation
Capability Path: `openspec/specs/drl-recommender/spec.md`

## Overview
Uses `GeminiRecommender` (connecting to Google Gemini API with a deterministic local fallback) and an interpretable preference vector `user_flavor_weights = [light_clean, bento_savory, high_protein]` to rank safe meal candidates, parse conversational intent, and continuously adapt to user feedback.

---

### Requirement: State & Action Space Representation
The system SHALL encode user context into an 8-dimensional normalized state vector and meal properties into a 6-dimensional action vector.

#### Scenario: State Vector Construction
- **GIVEN** time of day, dynamic target calories, steps, systolic BP, fasting glucose, and user flavor weights
- **WHEN** `encode_state()` is invoked
- **THEN** the state vector SHALL be normalized within numerical range $[0.0, 1.0]$

---

### Requirement: Multi-Objective Candidate Scoring
The system SHALL rank candidate meals using a balanced objective function combining preference/semantic score $Q$, nutritional fitness, and spatial distance penalty.

#### Scenario: Composite Score Evaluation
- **GIVEN** a candidate meal and target macronutrients
- **WHEN** `rank_meals()` is evaluated
- **THEN** $\text{Score} = (0.50 \times Q) + (0.35 \times \text{NutriFit}) - (0.15 \times \text{DistPenalty})$
- **AND** candidates SHALL be sorted in descending order of composite score

---

### Requirement: Closed-Loop Online Preference Feedback (Algorithm 3)
The system SHALL update `user_flavor_weights` immediately when human feedback is submitted via button click or natural language dialogue.

#### Scenario: Negative Feedback Adaptation ('Too Oily')
- **GIVEN** an active recommendation session where the user selects or says 'Too Oily / Too Heavy' (`too_oily`)
- **WHEN** feedback is processed by `handle_user_feedback()`
- **THEN** a reward signal $r_t = -0.6$ SHALL be assigned
- **AND** the savory flavor weight SHALL be decreased by $0.15$ and light/clean weight increased by $0.12$
