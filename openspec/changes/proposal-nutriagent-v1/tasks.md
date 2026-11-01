# OpenSpec Tasks: NutriAgent Initial Release
Change ID: `proposal-nutriagent-v1`

## 1. Domain Knowledge & Datasets Setup
- [x] 1.1 Create clinical health profiles (`data/sample_health_reports.json`) covering 5 distinct cohorts (Hypertension, Pre-diabetes, Gout, Fitness Athlete, Sedentary Student).
- [x] 1.2 Build Taiwanese external food & convenience store nutritional catalog (`data/meal_catalog.json`) with full macro/micronutrients, sodium, purine, GI, and GPS coordinates.

## 2. Clinical Rules Engine Implementation
- [x] 2.1 Implement `ClinicalRulesEngine` in `src/clinical_rules.py` with AHA DASH (sodium < 700mg, non-fried) and ADA diabetes guidelines.
- [x] 2.2 Enforce 0.0% Clinical Violation Rate (CVR) deterministic candidate pruning.

## 3. IoT Telemetry & Dynamic Energy Pipeline
- [x] 3.1 Implement `IoTPipeline` in `src/iot_pipeline.py` with Google Fit data ingestion.
- [x] 3.2 Implement Harris-Benedict BMR and dynamic TDEE computation with $0.65$ safety damping factor.
- [x] 3.3 Implement dynamic macronutrient target distribution ($C, P, F$) conditioned on clinical profile.

## 4. Geospatial LBS Engine
- [x] 4.1 Implement `SpatialLBSEngine` in `src/spatial_lbs.py` with great-circle Haversine distance calculations.
- [x] 4.2 Add walking duration estimation and auto-expansion fallback radius ($1.2\,\text{km} \rightarrow 2.5\,\text{km}$).

## 5. PyTorch Deep Reinforcement Learning Recommender
- [x] 5.1 Implement `NutriQNetwork` (MLP with LayerNorm & LeakyReLU) in `src/recommender.py`.
- [x] 5.2 Implement `ExperienceReplayBuffer` and state/action feature vector encoders.
- [x] 5.3 Implement multi-objective composite ranking function ($0.50 Q + 0.35 \text{NutriFit} - 0.15 \text{Dist}$).
- [x] 5.4 Implement online single-step mini-batch backpropagation for live feedback adaptation (`accept`, `too_oily`, `skip`).

## 6. Central Agent Orchestration & Interactive Web Cockpit
- [x] 6.1 Implement `NutriAgent` orchestrator in `src/agent.py` uniting the 8-stage pipeline and generating transparent clinical explanations.
- [x] 6.2 Develop interactive Flask Web Cockpit in `app.py` featuring glassmorphism design, real-time Google Fit dials, candidate cards, and live DRL preference weight monitors.

## 7. Verification & OpenSpec Documentation
- [x] 7.1 Author unit and integration test suite in `tests/test_agent.py` verifying clinical zero-violation, dynamic TDEE scaling, and DRL learning.
- [x] 7.2 Run and verify test suite passes (5/5 tests passing in 2.3s).
- [x] 7.3 Structure all project specifications under `openspec/` conforming to OpenSpec SDD standards (RFC 2119 keywords, BDD `GIVEN-WHEN-THEN` scenarios).
- [x] 7.4 Commit all changes to the local Git repository.
