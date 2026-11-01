# Capability: IoT Telemetry & Dynamic Metabolic Energy Pipeline
Capability Path: `openspec/specs/iot-telemetry/spec.md`

## Overview
Connects to Google Fit REST API (or high-fidelity sensor simulators) to stream user activity metrics and calculate dynamic TDEE and meal-specific caloric budgets.

---

### Requirement: Dynamic TDEE Calculation
The system SHALL compute Basal Metabolic Rate (BMR) and add active energy expenditure scaled by a safety damping factor.

#### Scenario: Real-time active calorie damping
- **GIVEN** user anthropometric attributes (weight, height, age, gender) and Google Fit active calories $C_{\text{act}}$
- **WHEN** the metabolic budget calculator executes
- **THEN** the system SHALL calculate BMR via the Mifflin-St Jeor equation
- **AND** the system SHALL compute $\text{Dynamic TDEE} = \text{BMR} + (0.65 \times C_{\text{act}})$
- **AND** the damping factor of $0.65$ SHALL be applied to avoid smartwatch calorie overcompensation

#### Scenario: Sedentary vs High Activity Budget Scaling
- **GIVEN** two identical user profiles, one with sedentary telemetry (1,850 steps) and one with high athletic telemetry (14,200 steps)
- **WHEN** the meal budget is allocated
- **THEN** the high activity meal budget SHALL be strictly greater than the sedentary meal budget

---

### Requirement: Macronutrient Goal Partitioning
The system SHALL partition target calories into carbohydrate, protein, and fat allocations according to clinical guidelines.

#### Scenario: Athletic profile protein boosting
- **GIVEN** a user with the athletic hyperactive condition
- **WHEN** macronutrients are calculated
- **THEN** protein ratio SHALL be at least $30\%$ of total caloric budget
- **AND** target protein SHALL be at least $30.0\,\text{g}$ per meal
