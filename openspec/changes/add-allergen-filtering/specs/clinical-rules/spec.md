# Delta Capability Spec: Clinical Rules - Food Allergen Gating
Capability Path: `openspec/specs/clinical-rules/spec.md`

## MODIFIED: Capability Overview
Extended deterministic clinical constraint gate to enforce both metabolic nutrition therapy (MNT) rules and zero-tolerance food allergen isolation.

---

### ADDED: Requirement: Food Allergen Pruning
The system SHALL evaluate candidate meals against user-declared food allergens and SHALL strictly reject any meal containing one or more matching allergens.

#### Scenario: Seafood and Shellfish Allergy Isolation
- **GIVEN** a user health profile with declared allergen `"seafood"`
- **WHEN** candidate meals are evaluated by the clinical rules engine
- **THEN** any meal containing `"seafood"`, `"fish"`, or `"shellfish"` in its `allergens` list SHALL be rejected
- **AND** the rejection explanation SHALL state: `違反食物過敏安全紅線: 餐點含有您過敏的食材 [海鮮/魚貝類]`
- **AND** the meal SHALL NOT appear in the Safe Candidate Pool

#### Scenario: Peanuts and Tree Nuts Allergy Isolation
- **GIVEN** a user health profile with declared allergen `"peanuts"`
- **WHEN** candidate meals are evaluated
- **THEN** any meal with `"peanuts"` or `"nuts"` in its `allergens` list SHALL be rejected

#### Scenario: Zero Allergen Violation Guarantee
- **GIVEN** any user profile with non-empty declared allergens
- **WHEN** the agent outputs Top-3 recommendations
- **THEN** none of the recommended meals SHALL contain any of the user's declared allergens
