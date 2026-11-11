# NutriAgent System Design Specification (DESIGN.md)

> **Document Version**: v2.0.0 (Synced with Updated Proposal DOCX + Gemini API + ChatGPT Conversational Agent UI)  
> **Course**: 物聯網應用與資料分析 (IoT Applications & Data Analysis) Final Project  
> **Standard**: *100% Reproducibility, Zero Clinical/Allergen Regression (CVR = 0.0%, AVR = 0.0%), Grounded Conversational AI.*

---

## 1. Architecture Overview

NutriAgent implements an 8-stage Domain AI Agent pipeline combining deterministic medical safety with Google Gemini API conversational intelligence:

```
[User Chat / Context] → [IoT Adapter & Plausibility Check] → [Dynamic TDEE (0.65 Damping & 900 kcal Cap)]
        ↓
[Spatial LBS (1.2km → 2.5km)] → [Deterministic Clinical & TFDA-11 Allergen Gate (Never Relax)]
        ↓
[Gemini API Contextual Ranking & Grounded Dialogue] → [ChatGPT-Style Conversational Web UI]
```

### Module Breakdown
1. [`src/iot_pipeline.py`](file:///c:/Users/User/Desktop/物聯網應用與資料分析/FinalProject/src/iot_pipeline.py): Wearable IoT Adapter (Android Health Connect / Apple HealthKit simulator), timeout fallback (`LOW_CONF`), cross-sensor plausibility check (`plausibility_check` comparing steps vs. heart rate), Mifflin-St Jeor BMR, 0.65 damping factor, and 900 kcal single-meal cap.
2. [`src/clinical_rules.py`](file:///c:/Users/User/Desktop/物聯網應用與資料分析/FinalProject/src/clinical_rules.py): Deterministic MNT constraint gate (2025 AHA/ACC Hypertension sodium ≤ 700mg & non-fried, ADA 2026 Pre-diabetes Low/Med GI & added sugar ≤ 5g, 2020 ACR Gout non-High purine, LDL-C saturated fat ≤ 5g, CKD eGFR < 60) and **TFDA 11 mandatory allergen categories**. Includes `generate_order_tips()` when safe pool is empty.
3. [`src/spatial_lbs.py`](file:///c:/Users/User/Desktop/物聯網應用與資料分析/FinalProject/src/spatial_lbs.py): Haversine distance calculation with automatic radius expansion (`1.2 km` → `2.5 km` when `< 4` candidates).
4. [`src/recommender.py`](file:///c:/Users/User/Desktop/物聯網應用與資料分析/FinalProject/src/recommender.py): `GeminiRecommender` connecting to Google Gemini API (`gemini-2.5-flash` / `gemini-2.0-flash`) for natural language intent extraction, semantic craving alignment, online preference weight updates (`user_flavor_weights`), and grounded conversational response generation.
5. [`src/agent.py`](file:///c:/Users/User/Desktop/物聯網應用與資料分析/FinalProject/src/agent.py): Central orchestrator implementing `run_recommendation()`, `chat()`, numerical consistency verification (`verify_explanation_consistency`), and multi-turn conversation memory.
6. [`app.py`](file:///c:/Users/User/Desktop/物聯網應用與資料分析/FinalProject/app.py): ChatGPT-style conversational AI web interface with collapsible reasoning traces, embedded Top-3 meal cards, quick prompt chips, and sidebar configuration for Gemini API Key, clinical profiles, and TFDA-11 allergens.

---

## 2. How to Run & Verify

```powershell
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run automated unit tests (9 tests covering clinical gate, TFDA-11 allergens, plausibility check, and chat agent)
python -m unittest tests/test_agent.py

# 3. Run quantitative KPI benchmark suite
python benchmark.py

# 4. Run CLI conversational demo
python demo_run.py

# 5. Launch ChatGPT-style Conversational Web UI
python app.py
# Open http://127.0.0.1:5000 in your browser
```
