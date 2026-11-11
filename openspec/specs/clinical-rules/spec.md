# Capability: Clinical Rules & Medical Nutrition Therapy (MNT)
Capability Path: `openspec/specs/clinical-rules/spec.md`

## Overview
Enforces deterministic clinical constraint gating to prune meals that violate user health checkup red flags and declared food allergens before recommendation scoring.

---

### Requirement: Clinical Hard-Constraint Pruning
The system SHALL evaluate candidate meals against user clinical checkup metrics and SHALL reject any meal violating safety thresholds with zero exceptions.

#### Scenario: Stage-1 Hypertension Sodium and Fat Restriction
- **GIVEN** a user health profile with systolic blood pressure $\ge 130\,\text{mmHg}$ or diastolic $\ge 85\,\text{mmHg}$
- **WHEN** the clinical rules engine filters candidate meals
- **THEN** every accepted meal in the Safe Candidate Pool SHALL have sodium content $\le 700\,\text{mg}$
- **AND** the system SHALL reject all deep-fried meals (`is_deep_fried == True`)

#### Scenario: Pre-Diabetes and Insulin Resistance Restriction
- **GIVEN** a user health profile with fasting blood glucose $\ge 100\,\text{mg/dL}$
- **WHEN** candidate meals are evaluated
- **THEN** any meal labeled with High Glycemic Index (`glycemic_index == "High"`) SHALL be rejected
- **AND** any meal with added sugar $> 5.0\,\text{g}$ SHALL be rejected

#### Scenario: Hyperuricemia and Gout Protection
- **GIVEN** a user health profile with serum uric acid $\ge 7.0\,\text{mg/dL}$
- **WHEN** candidate meals are evaluated
- **THEN** any meal labeled with High Purine level (`purine_level == "High"`) SHALL be rejected

#### Scenario: Hyperlipidemia Lipoprotein Control
- **GIVEN** a user health profile with LDL cholesterol $\ge 130\,\text{mg/dL}$
- **WHEN** candidate meals are evaluated
- **THEN** any meal with saturated fat $> 5.0\,\text{g}$ SHALL be rejected

---

### Requirement: Food Allergen Gating
The system SHALL accept user-declared food allergens and SHALL strictly reject any candidate meal containing one or more of the specified allergens.

#### Scenario: Seafood Allergy Isolation
- **GIVEN** a user health profile with declared allergen `"seafood"`
- **WHEN** candidate meals are evaluated
- **THEN** any meal containing `"seafood"`, `"fish"`, or `"shellfish"` in its `allergens` list SHALL be rejected
- **AND** the rejection explanation SHALL state that the meal contains the allergen

#### Scenario: Peanuts and Tree Nuts Allergy Isolation
- **GIVEN** a user profile with declared allergen `"peanuts"`
- **WHEN** candidate meals are evaluated
- **THEN** any meal with `"peanuts"` or `"nuts"` in its `allergens` list SHALL be rejected

---

### Requirement: Zero Clinical Violation Rate (CVR)
The system SHALL maintain a Clinical Violation Rate (CVR) of exactly $0.0\%$ in all final recommendations, encompassing both medical conditions and declared food allergens.

#### Scenario: Verification of zero violation across patient cohorts
- **GIVEN** synthetic test profiles across hypertension, pre-diabetes, gout, and allergen constraints
- **WHEN** recommendations are produced by the agent
- **THEN** none of the recommended Top-3 meals SHALL violate the user's clinical conditions or allergen declarations
