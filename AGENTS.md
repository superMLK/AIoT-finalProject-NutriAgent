# AGENTS.md - Developer & AI Agent Collaboration Directive

> **Target Audience**: AI Coding Assistants (Antigravity, Cursor, Claude Code, Cline, GitHub Copilot, Windsurf) and Human Successors.  
> **Repository Standard**: Spec-Driven Development via **OpenSpec (v1.0)** — Current Architecture Version: **v2.0 (Gemini API + ChatGPT-style Conversational Agent + Updated Proposal DOCX Sync)**.  
> **Core Mandate**: *Any AI agent modifying or optimizing this repository SHALL follow this protocol to ensure 100% reproducibility, zero clinical/allergen regression (`CVR = 0.0%`, `AVR = 0.0%`), numerical consistency (`numbers_in(E) == db_values(R)`), and clean handover.*

---

## 1. System Identity & Architecture Map (v2.0 Current State)

* **System Name**: **NutriAgent** (Domain AI Agent for Real-Time Wearable IoT & Clinical Dietary Decision)
* **Core Paradigm**: `AI Agent + Domain Knowledge + Data Analytics + Real-World Application`
* **Architecture Flow (Algorithm 1–3 from `NutriAgent_Proposal.docx` + Gemini Conversational Agent)**:
  $$\text{User Chat / Context} \rightarrow \text{IoT Adapter \& Plausibility Check} \rightarrow \text{Dynamic TDEE (0.65 Damping \& 900 kcal Cap)} \rightarrow \text{Spatial LBS (1.2km/2.5km)} \rightarrow \text{Deterministic Clinical \& TFDA-11 Allergen Hard Gate (Never Relax)} \rightarrow \text{Gemini API Contextual Ranking \& Grounded Dialogue} \rightarrow \text{ChatGPT-Style UI \& Closed-Loop Feedback}$$

### What Was Completed in v2.0 (`openspec/changes/gemini-chat-agent-v2`)
1. **Synced with Updated `NutriAgent_Proposal.docx`**:
   - **Never-Relax Safety Gate**: Removed the legacy fallback that relaxed rules when `SafePool` was empty. Now returns `status="no_compliant_meal"` with actionable `order_tips` (`src/clinical_rules.py`, `src/agent.py`).
   - **TFDA 11 Mandatory Allergens**: Expanded allergen alias taxonomy to cover all 11 Taiwan FDA mandatory categories (`crustacean`, `mango`, `peanuts`, `dairy`, `egg`, `tree_nuts`, `sesame`, `gluten`, `soy`, `fish`, `sulfites`) plus composite `"seafood"`.
   - **CKD Rule**: Added Chronic Kidney Disease (`eGFR < 60`) high-potassium / high-phosphorus restriction.
   - **IoT Plausibility Check & 900 kcal Cap**: Added `plausibility_check()` (filtering vehicle vibration step artifacts by comparing step count against heart rate), `LOW_CONF` offline fallback flag, and single-meal `900.0 kcal` physiological cap (`src/iot_pipeline.py`).
   - **Numerical Consistency Verification**: Added `NutriAgent.verify_explanation_consistency()` enforcing `assert numbers_in(E) == db_values(R)`.
2. **Replaced PyTorch Neural Network with Google Gemini API (`src/recommender.py`)**:
   - Removed `torch` / `NutriQNetwork` dependency.
   - Implemented `GeminiRecommender` (aliased as `DRLRecommender` for backward compatibility) connecting to Google Gemini REST API (`gemini-2.5-flash` / `gemini-2.0-flash`) for NLU intent parsing, semantic craving scoring, online preference weight updates (`user_flavor_weights = [light_clean, bento_savory, high_protein]`), and grounded conversational response generation. Includes a deterministic zero-latency local fallback when `GEMINI_API_KEY` is not set.
3. **Upgraded `app.py` to a ChatGPT-Style Conversational AI Agent UI**:
   - Multi-turn chat interface (`/api/chat`, `/api/config`, `/api/recommend`, `/api/feedback`) with collapsible 8-stage Agent Reasoning Trace, embedded interactive Top-3 meal cards, prompt chips, and sidebar controls for Gemini API Key, clinical profiles, and TFDA-11 allergens.

### File Responsibilities
```
FinalProject/
├── AGENTS.md                  # <-- Universal AI Agent Protocol & Handover Roadmap
├── HANDOVER.md                # Human & cross-machine onboarding guide
├── PROPOSAL.md & DESIGN.md    # Synced specification documents matching NutriAgent_Proposal.docx
├── NutriAgent_Proposal.docx   # Official updated Proposal Word document (Source of Truth for academic spec)
├── benchmark.py               # Objective KPI benchmark suite (Outputs machine-readable JSON for agents)
├── demo_run.py                # Standalone CLI multi-turn conversational execution script (UTF-8 safe)
├── app.py                     # ChatGPT-style Conversational Agent Web UI (Flask + Gemini API)
├── src/
│   ├── clinical_rules.py      # Deterministic MNT (AHA/ADA/ACR/CKD) & TFDA-11 Allergen Hard Gate + order_tips
│   ├── iot_pipeline.py        # Wearable IoT Adapter, plausibility_check, Mifflin-St Jeor BMR & 900 kcal cap
│   ├── spatial_lbs.py         # Haversine spatial indexing & 1.2km -> 2.5km radius expansion
│   ├── recommender.py         # GeminiRecommender (Google Gemini API + Online Bandit Preference Weights)
│   └── agent.py               # Central 8-stage orchestrator, chat() entrypoint & numerical consistency verifier
├── data/
│   ├── sample_health_reports.json  # 5 clinical test cohorts
│   └── meal_catalog.json           # 14 Taiwan convenience & bento meals with full nutrition & allergens
├── openspec/                  # OpenSpec Source-of-Truth
│   ├── config.yaml            # Project configuration & standard declaration
│   ├── specs/                 # Permanent baseline capability contracts
│   └── changes/               # Versioned change proposals (including gemini-chat-agent-v2)
├── .agents/skills/            # Exported Workspace Agent Skills (Auto-discovered by Antigravity/Agents)
│   ├── clinical-iot-dietary-guardrail/SKILL.md      # Clinical MNT gate, TFDA-11 allergens & IoT plausibility check
│   └── gemini-grounded-conversational-agent/SKILL.md # Gemini REST client, numerical grounding & ChatGPT UI pattern
└── tests/
    └── test_agent.py          # Automated verification suite (9/9 passing)
```

---

## 2. Non-Negotiable Invariants (Golden Rules for AI Agents)

When any AI agent modifies or optimizes this codebase, it **MUST NOT** violate these 5 invariants:

1. **Clinical Safety Hard Gating (`CVR = 0.0%`) & Never-Relax Rule**:
   - The clinical filter in `src/clinical_rules.py` is a *deterministic boundary* executed **before** any LLM/Gemini scoring.
   - When `SafePool` is empty, the system **SHALL NEVER** relax clinical or allergen rules; it **MUST** return `status = "no_compliant_meal"` and `order_tips`.
   - Hypertension profiles ($\text{SBP} \ge 130$ or $\text{DBP} \ge 85$) **SHALL NEVER** receive meals with sodium $> 700\,\text{mg}$ or deep-fried items.
   - Gout profiles ($\text{UA} \ge 7.0$) **SHALL NEVER** receive High Purine meals.
2. **Zero Allergen Exposure (`AVR = 0.0%`, TFDA 11 Categories)**:
   - Any meal containing an allergen declared by the user (or its alias in `ALLERGEN_ALIAS_MAP`) **SHALL BE PRUNED IMMEDIATELY** before ranking.
3. **Strict Numerical Grounding (`numbers_in(E) == db_values(R)`)**:
   - All nutritional figures (calories, protein, fat, sodium, price, distance) in explanations and chat responses **MUST** come strictly from `meal_catalog.json` and pass `verify_explanation_consistency()`.
4. **Offline & API-Key Resilience**:
   - `benchmark.py`, `demo_run.py`, `tests/test_agent.py`, and `app.py` **MUST** work with zero errors even when `GEMINI_API_KEY` is not set in the environment (using the deterministic grounded engine in `GeminiRecommender`), and seamlessly switch to live Google Gemini API calls when `GEMINI_API_KEY` is provided.
5. **No Hardcoded Absolute Paths & UTF-8 Console Safety**:
   - All file operations **SHALL** use `pathlib.Path(__file__).resolve().parent...` and CLI scripts **SHALL** enforce UTF-8 stdout encoding.

---

## 3. OpenSpec Workflow for AI Agents

Do not write code directly from ungrounded prompts ("vibe coding"). Follow the 5-step OpenSpec pipeline:

```
[1. Explore & Benchmark] → [2. OpenSpec Change Proposal] → [3. Implement Tasks] → [4. Verify Tests] → [5. Benchmark Comparison]
```

1. **Step 1 - Benchmark Current State**:
   Run `python benchmark.py` to capture baseline metrics (`cvr = 0.0%`, `avr = 0.0%`, `caloric_mae_kcal = 114.48`, `mean_latency_ms = 0.21`).
2. **Step 2 - Create OpenSpec Change Package**:
   Create a new directory `openspec/changes/<your-feature-name>/` with `.openspec.yaml`, `proposal.md`, `specs/<capability>/spec.md`, `design.md`, and `tasks.md`.
3. **Step 3 - Implement Changes**:
   Edit source files in `src/` or `app.py`, checking off items in `tasks.md`.
4. **Step 4 - Run Unit Tests**:
   Run `python -m unittest tests/test_agent.py` (all 9+ tests **MUST** pass).
5. **Step 5 - Run Benchmark & Compare**:
   Run `python benchmark.py` and confirm `benchmark_status == "PASSED"`.

---

## 4. Prioritized Next Tracks for Successor AI Agents

The next AI Agent picking up this project can immediately implement any of the following tracks aligned with `NutriAgent_Proposal.docx` Section 5.6:

### Track 1: Expand Taiwan Dining Dataset to 200+ Meals & 50 Synthetic Clinical Profiles
* **Goal**: Fulfill the full experimental dataset scale specified in `NutriAgent_Proposal.docx` Section 5.6 (1).
* **Tasks**:
  - Expand `data/meal_catalog.json` from 14 prototype items to $\ge 200$ real items from 7-Eleven, FamilyMart, Liang She Han, Subway, Sukiya, Louisa Coffee, etc., including `potassium_level` and `phosphorus_level` for CKD testing.
  - Expand `data/sample_health_reports.json` (or create `data/synthetic_50_profiles.json`) with 50 synthetic clinical profiles (10 per cohort: Hypertension, Pre-diabetes, Gout, Athletic, Healthy Control).

### Track 2: Gemini Multimodal Vision Food Label / Menu OCR Ingestion
* **Goal**: Allow users in the ChatGPT-style UI (`app.py`) to upload a photo of a convenience store nutrition label or restaurant menu, or a health checkup report image.
* **Tasks**:
  - Add image upload support to the chat input dock in `app.py`.
  - Use Gemini Multimodal API (`inlineData` base64 image in `GeminiRecommender._call_gemini_api`) to extract structured nutrition facts (`calories_kcal`, `sodium_mg`, `protein_g`, `allergens`) and run them through `ClinicalRulesEngine.evaluate_meal_safety()` in real time.

### Track 3: Experimental Baselines & Ablation Study Harness (`experiments.py`)
* **Goal**: Implement the 4 baselines defined in `NutriAgent_Proposal.docx` Section 5.6 (2) (`B1 Nearest/Popular`, `B2 Static Calorie Rule`, `B3 Pure LLM Zero-Shot without Clinical Gate`, `B4 Ablation: Recommender without Clinical Gate`).
* **Tasks**:
  - Create `experiments.py` to compare `NutriAgent` against `B1–B4` across CVR, AVR, Caloric MAE, Latency, and 5-step Preference Convergence, exporting a Markdown/CSV table ready for the final report.

### Track 4: Persistent Per-User SQLite Conversation & Preference Memory
* **Goal**: Upgrade in-memory `conversation_history` and `user_flavor_weights` to a local SQLite database (`data/nutriagent_state.db`) per `NutriAgent_Proposal.docx` Table 5-2.
* **Tasks**:
  - Persist per-profile `user_flavor_weights`, `InteractionMemoryBuffer`, and multi-session chat histories in SQLite so preferences survive server restarts.

---

## 5. Verification Commands for AI Agents

```bash
# 1. Run full unit test suite (9/9 tests must pass)
python -m unittest tests/test_agent.py

# 2. Run automated KPI benchmark (Outputs JSON between [AGENT_JSON_OUTPUT_START/END])
python benchmark.py

# 3. Run end-to-end multi-turn conversational CLI demo
python demo_run.py

# 4. Verify Flask ChatGPT UI & /api/chat endpoint headless
python -c "from app import app; c = app.test_client(); r = c.post('/api/chat', json={'message': '推薦公館午餐', 'profile_id': 'P_001_HYPERTENSION'}); assert r.status_code == 200 and r.get_json()['status'] == 'success'; print('Chat UI & API Verified!')"
```
