# NutriAgent System Design Specification (DESIGN.md)

> **Document Version**: v1.0.0 (Proposal Stage)  
> **Course**: 物聯網應用與資料分析 (IoT Applications & Data Analysis) Final Project  
> **Target Audience**: Developers, Evaluators, and Successor Engineers  
> **Standard**: *A successor developer must be able to understand, execute, verify, and extend this project without the original author.*

---

## 1. Problem Statement & Motivation
* **Context**: Over 72.8% of Taiwanese urban adults rely on external dining (外食) for at least two meals a day, contributing to a 34.6% prevalence of metabolic syndrome.
* **Core Pain Point**: Daily food selection suffers from "Decision Paralysis" and metabolic mismatch. Existing fitness apps require tedious manual logging, general LLMs suffer from numerical nutritional hallucinations, and commercial delivery apps prioritize sales over health metrics.
* **Mission**: Build **NutriAgent**, a real-time, context-aware Domain AI Agent that bridges wearable IoT telemetry (Google Fit), clinical health checkup red flags, and local physical restaurant menus (LBS) via Deep Reinforcement Learning (DRL) and clinical hard-constraint pruning.

---

## 2. Requirements & Specification

### 2.1 Functional Requirements (FR)
* **FR-1 [IoT Activity Sync]**: Automatically ingest real-time step counts, heart rate, and active energy expenditure (kcal) via Google Fit REST API (with offline synthetic mock fallback).
* **FR-2 [Clinical Report Parsing & Guardrails]**: Accept structured health checkup reports (Blood Pressure, Fasting Glucose, Lipid Panel, Uric Acid, BMI) and enforce strict medical nutrition therapy (MNT) hard boundaries.
* **FR-3 [Spatial Restaurant & Menu Retrieval]**: Identify physical food choices within a 1.0 km radius (convenience stores: 7-Eleven, FamilyMart; chain bento stores: Liang She Han, Subway, etc.).
* **FR-4 [Adaptive Preference Modeling via DRL]**: Implement a Deep Q-Network (DQN) / Contextual Bandit policy that balances immediate nutritional compliance with dynamic user flavor preferences.
* **FR-5 [Explainable Recommendation Interface]**: Provide top-3 meal suggestions with transparent clinical rationales and capture closed-loop user feedback (Accept, Reject, Too Oily, Swap).
* **FR-6 [Food Allergen Input & Gating]**: Accept user-declared food allergens (seafood, peanuts, gluten, dairy, egg, soy, sesame) and enforce zero-tolerance pruning so meals with conflicting allergens are strictly excluded.

### 2.2 Non-Functional Requirements (NFR)
* **NFR-1 [Clinical Safety Assurance]**: 0.0% Clinical Violation Rate (CVR). Under no circumstances may a high-sodium meal be recommended to a stage-2 hypertension profile.
* **NFR-2 [Inference Latency]**: End-to-end recommendation response time < 800 ms on consumer-grade CPU.
* **NFR-3 [Reproducibility & Modularity]**: Clean separation of clinical rules, AI models, data pipelines, and UI.

---

## 3. High-Level Architecture

The system follows the 8-stage Domain AI Agent processing paradigm:

```
[User & Context] → [Multimodal Input] → [Planner Agent] → [Retrieval & LBS]
        ↓
[Clinical Hard-Constraint Gate] → [DRL Recommendation Engine] → [Explainable Decision] → [Streamlit UI & Feedback]
```

### Module Breakdown:
1. `src/iot_pipeline.py`: Google Fit OAuth 2.0 client & synthetic circadian activity generator.
2. `src/clinical_rules.py`: Deterministic Medical Nutrition Therapy (MNT) constraint checker.
3. `src/spatial_lbs.py`: Spatial indexing (Haversine/KD-Tree) and food database loader.
4. `src/recommender.py`: PyTorch Deep Q-Network (DQN) policy network and experience replay buffer.
5. `src/agent.py`: Central orchestrator uniting state encoding, hard filtering, scoring, and explanation.
6. `app.py`: Streamlit-based interactive web cockpit with spatial map rendering and telemetry dials.

---

## 4. Data Models & Schemas

### 4.1 Health Checkup Profile Schema (`data/sample_health_reports.json`)
```json
{
  "profile_id": "P_001_HYPERTENSION",
  "name": "陳先生 (42歲 上班族)",
  "metrics": {
    "blood_pressure_systolic": 142,
    "blood_pressure_diastolic": 92,
    "fasting_glucose_mg_dl": 98,
    "total_cholesterol_mg_dl": 210,
    "ldl_c_mg_dl": 135,
    "uric_acid_mg_dl": 6.2,
    "bmi": 26.4
  },
  "clinical_conditions": ["Hypertension_Stage1", "Hyperlipidemia_Borderline"],
  "dietary_hard_constraints": {
    "max_meal_sodium_mg": 700,
    "prohibit_deep_fried": true,
    "max_saturated_fat_g": 5.0
  }
}
```

### 4.2 Food & Meal Database Schema (`data/meal_catalog.json`)
```json
{
  "item_id": "711_CHICKEN_QUINOA",
  "store_name": "7-Eleven 鑫公館門市",
  "category": "Convenience_Store",
  "dish_name": "義式烤雞藜麥健康餐盒",
  "coordinates": {"lat": 25.0152, "lon": 121.5332},
  "nutrition": {
    "calories_kcal": 465,
    "protein_g": 28.5,
    "fat_g": 11.2,
    "saturated_fat_g": 2.8,
    "carbohydrates_g": 62.0,
    "dietary_fiber_g": 6.5,
    "sodium_mg": 580,
    "glycemic_index": "Low",
    "purine_level": "Low"
  },
  "tags": ["Low_Sodium", "High_Protein", "Low_GI", "Non_Fried"],
  "price_twd": 99
}
```

---

## 5. Mathematical & Algorithmic Formulation

### 5.1 Dynamic Caloric Budgeting
Given user weight $W$ (kg), height $H$ (cm), age $A$ (yr), and Google Fit cumulative active burn $C_{\text{act}}$:
$$\text{BMR} = 10 \cdot W + 6.25 \cdot H - 5 \cdot A + s \quad (s = +5 \text{ for male}, -161 \text{ for female})$$
$$\text{Dynamic TDEE} = \text{BMR} + \alpha \cdot C_{\text{act}} \quad (\alpha = 0.65 \text{ safety damping factor})$$
Meal Target for lunch/dinner:
$$\text{Target}_{\text{meal}} = \text{Dynamic TDEE} \times 0.35$$

### 5.2 Reinforcement Learning Formulation
* **State $s_t \in \mathbb{R}^8$**:
  $$s_t = \left[ \text{TimeOfDay}, \frac{\text{Target}_{\text{meal}}}{1000}, \frac{\text{Steps}}{10000}, \frac{\text{BP}_{\text{sys}}}{180}, \frac{\text{FG}}{200}, \text{Pref}_{\text{bento}}, \text{Pref}_{\text{light}}, \text{Pref}_{\text{noodle}} \right]$$
* **Action $a \in \mathcal{A}$**: Selection of a meal candidate $i$ from the filtered safe pool $\mathcal{S}_{\text{safe}}$.
* **Composite Scoring Function**:
  $$\text{Score}(s_t, a_i) = w_1 \cdot Q_\theta(s_t, a_i) + w_2 \cdot \text{NutriFit}(a_i, \mathbf{m}^*) - w_3 \cdot \text{Dist}(u, a_i)$$
  where $\mathbf{m}^*$ is the target macronutrient vector and $Q_\theta$ is parameterized by a 3-layer MLP.

---

## 6. How to Run & Verify

### 6.1 Prerequisites
* Python 3.10+
* Virtual Environment Recommended

### 6.2 Installation
```powershell
pip install -r requirements.txt
```

### 6.3 Quick Execution
```powershell
# Run the interactive Streamlit Web Cockpit
streamlit run app.py
```

### 6.4 Automated Verification Tests
```powershell
# Run test suite to verify clinical constraint masking & DRL convergence
python -m unittest discover tests
```

---

## 7. Results & Limitations

### 7.1 Key Validation Results
* **Clinical Safety**: 100% rejection of >700mg sodium meals for Stage 1/2 Hypertension test fixtures.
* **Dynamic Budgeting**: Real-time response to simulated 10,000 steps vs. 1,500 sedentary steps adjusting meal calories by ~180 kcal.
* **RL Policy Adaptation**: Within 5 user interaction cycles ("Too Oily" signal), oily bento recommendations drop by >80%.

### 7.2 Current Limitations & Roadmap
* **LBS Scope**: Currently indexed for key university & business districts in Taipei; needs global Google Places API key for arbitrary worldwide coordinates.
* **Wearable Connectivity**: Google Fit is migrating toward Android Health Connect; future iterations will adopt the unified Health Connect SDK.
