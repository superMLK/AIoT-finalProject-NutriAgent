# Capability: Clinical Rules & Medical Nutrition Therapy (MNT)
Capability Path: `openspec/specs/clinical-rules/spec.md`

## Overview
Enforces deterministic clinical constraint gating to prune meals that violate user health checkup red flags before recommendation scoring.

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

### Requirement: Zero Clinical Violation Rate (CVR)
The system SHALL maintain a Clinical Violation Rate (CVR) of exactly $0.0\%$ in all final recommendations.

#### Scenario: Verification of zero violation across patient cohorts
- **GIVEN** synthetic test profiles across hypertension, pre-diabetes, and gout
- **WHEN** recommendations are produced by the agent
- **THEN** none of the recommended Top-3 meals SHALL violate the user's clinical conditions
