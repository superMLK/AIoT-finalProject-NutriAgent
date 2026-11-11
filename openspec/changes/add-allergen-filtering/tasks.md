# OpenSpec Tasks: Food Allergen Filtering
Change ID: `add-allergen-filtering`

## Implementation Checklist
- [x] 1. Data Schema Updates
  - [x] 1.1 Add `allergens` field to user profiles in `data/sample_health_reports.json`.
  - [x] 1.2 Add standardized `allergens` tags to all meals in `data/meal_catalog.json`.
- [x] 2. Clinical Rules Engine Extension
  - [x] 2.1 Define `ALLERGEN_ALIAS_MAP` in `src/clinical_rules.py`.
  - [x] 2.2 Implement allergen conflict detection inside `evaluate_meal_safety()`.
- [x] 3. Agent Integration
  - [x] 3.1 Accept dynamic `custom_allergens` in `NutriAgent.run_recommendation()`.
  - [x] 3.2 Add allergen clearance annotation to recommendation explanations.
- [x] 4. Web Cockpit UI & API
  - [x] 4.1 Add allergen checkboxes in `app.py` HTML template.
  - [x] 4.2 Support `allergens` parameter in `/api/recommend`.
  - [x] 4.3 Display allergen tags on meal cards.
- [x] 5. Automated Verification
  - [x] 5.1 Add test case in `tests/test_agent.py` asserting zero allergen violations.
  - [x] 5.2 Update global spec `openspec/specs/clinical-rules/spec.md`.
  - [x] 5.3 Verify all tests pass and commit to Git.
