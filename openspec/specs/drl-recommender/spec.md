# Capability: Deep Reinforcement Learning (DRL) Recommender
Capability Path: `openspec/specs/drl-recommender/spec.md`

## Overview
Uses a PyTorch-based Deep Q-Network (DQN) with an experience replay buffer to rank safe meal candidates and continuously adapt to user flavor preferences.

---

### Requirement: State & Action Space Representation
The system SHALL encode user context into an 8-dimensional normalized state vector and meal properties into a 6-dimensional action vector.

#### Scenario: State Vector Construction
- **GIVEN** time of day, dynamic target calories, steps, systolic BP, fasting glucose, and user flavor weights
- **WHEN** the agent prepares input for the DQN policy network
- **THEN** the state vector SHALL be normalized within numerical range $[0.0, 1.0]$

---

### Requirement: Multi-Objective Candidate Scoring
The system SHALL rank candidate meals using a balanced objective function combining Q-value, nutritional fitness, and spatial distance penalty.

#### Scenario: Composite Score Evaluation
- **GIVEN** a candidate meal and target macronutrients
- **WHEN** the scoring function is evaluated
- **THEN** $\text{Score} = (0.50 \times Q) + (0.35 \times \text{NutriFit}) - (0.15 \times \text{DistPenalty})$
- **AND** candidates SHALL be sorted in descending order of composite score

---

### Requirement: Closed-Loop Online Learning Feedback
The system SHALL update the Q-network weights and flavor preferences immediately when human feedback is submitted.

#### Scenario: Negative Feedback Adaptation ('Too Oily')
- **GIVEN** an active recommendation session where the user selects 'Too Oily / Too Heavy'
- **WHEN** feedback is processed by `handle_user_feedback`
- **THEN** a reward signal $r_t = -0.6$ SHALL be assigned
- **AND** the transition $(s_t, a_t, r_t, s_{t+1})$ SHALL be added to the Replay Buffer
- **AND** the savory flavor weight SHALL be decreased by at least $0.10$
- **AND** PyTorch backpropagation SHALL execute a mini-batch gradient update
