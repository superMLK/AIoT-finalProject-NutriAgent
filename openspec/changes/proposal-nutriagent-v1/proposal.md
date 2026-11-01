# OpenSpec Change Proposal: NutriAgent Initial Release
Change ID: `proposal-nutriagent-v1`

## 1. Why & Motivation (The Problem)
* **Real-World Context**: Over 72.8% of Taiwanese urban adults rely on external dining (外食) for at least two meals a day, contributing to a 34.6% prevalence of metabolic syndrome (Taiwan MOHW & WHO, 2024–2026).
* **Research Gaps & Pain Points**:
  1. *Passive Calorie Trackers (e.g. MyFitnessPal)*: Rely on tedious manual weighing and food logging with >80% user churn within 30 days; offer zero proactive guidance at decision time.
  2. *General LLMs (e.g. ChatGPT)*: Lack real-time consumer IoT wearable telemetry, lack physical geospatial coordinates, and suffer from nutritional numerical hallucinations.
  3. *Commercial Food Delivery (e.g. UberEats/Google Maps)*: Optimize purely for ad clicks and profit, aggressively promoting high-calorie, deep-fried meals with complete disregard for user clinical red flags (hypertension, pre-diabetes, gout).

## 2. What (Proposed Solution)
We propose **NutriAgent**, a real-time, context-aware Domain AI Agent integrating:
1. **Google Fit Wearable Telemetry**: Minute-level activity tracking to dynamically adjust total daily energy expenditure (Dynamic TDEE) with safety damping ($\alpha=0.65$).
2. **Clinical Hard-Constraint Gating**: Deterministic Medical Nutrition Therapy (MNT) rules ensuring a 0.0% Clinical Violation Rate (CVR).
3. **Deep Reinforcement Learning (DRL)**: PyTorch Deep Q-Network (DQN) with an experience replay buffer that adapts to user flavor preferences on-the-fly.
4. **Spatial LBS Menu Graph**: Real-time walking radius query of convenience stores and chain restaurants with verified nutrition facts.

---

## 3. Scope Specification
* **In-Scope**:
  - Ingestion of Google Fit step counts, active energy burned, and dynamic metabolic budgeting.
  - Multi-profile clinical evaluation (Stage 1/2 Hypertension, Pre-Diabetes, Hyperuricemia/Gout, Athletic, Sedentary Healthy).
  - PyTorch DQN inference, loss backpropagation, and flavor preference weight adaptation.
  - Spatial Haversine distance computation within 1.0–2.5 km radius in Taipei commercial zones.
  - Interactive Web Cockpit powered by Flask and comprehensive automated unit test suite.
* **Out-of-Scope**:
  - Direct write-back integration to hospital Electronic Health Record (EHR) databases.
  - Invasive Continuous Glucose Monitoring (CGM) subcutaneous sensor hardware pairing.

---

## 4. Course Alignment Specification (10% Final Project Proposal)

### 4.1 Abstract (A–F Six-Part Story)
* **A. Attention Getter**: 34.6% metabolic syndrome in Taiwan; >72.8% external diners; 45% smartwatch adoption.
* **B. But (Challenge)**: Passive tracking churn; LLM numerical hallucinations; commercial delivery misalignment.
* **C. Cure (Solution)**: NutriAgent Domain AI Agent.
* **D. Development (Method)**: Dynamic TDEE + Clinical Hard Masking + PyTorch DQN + Spatial LBS.
* **E. Experiments (Evaluation)**: 50 synthetic clinical profiles, 500+ Taiwanese meals, evaluated against 3 baselines.
* **F. Findings (Expected Outcomes)**: 100% clinical safety adherence, MAE < 5% caloric target error, +40% user satisfaction.

### 4.2 Introduction (A–F Structure)
* **A. Attention Getter**: Trillion-dollar external dining market; hypertension prevalence (26.8%), hyperlipidemia (25.6%), hyperglycemia (11.1%).
* **B. Background**: Consumer IoT maturity + Taiwan FDA open food composition database.
* **C. Problem**: Metabolic budget mismatch, clinical disconnect, spatial compromise.
* **D. Existing Limitations**: Passive apps, generic LLMs, commercial profit engines.
* **E. Innovation**: Multi-modal hard-soft fusion, IoT dynamic flux, explainable DRL feedback loop.
* **F. Contributions**: Domain AI Agent paradigm, Taiwan meal knowledge graph, clinical dynamic algorithm, reproducible open-source release.

### 4.3 Related Work & Summary Table
* 50% AI Recommender Literature (DRL, Two-Tower NCF, MLLM Knowledge Graphs) + 50% Clinical Nutrition Know-How (DASH, ADA, METs, Glycemic Index).
* Article Summary Table covering 6 authoritative 2024–2026 publications (JMIR, IEEE TMM, ACM TIST, The Lancet).
* Clear Research Gap derivation: `Existing Research → Limitations → Research Gap → Our Project`.

### 4.4 Deep Research: 3 Core Questions
* **Q1. 5 Core Mindsets**:
  1. Dynamic Energy Flux vs. Static Caloric Deficit
  2. Clinical Safety Hard Constraints Precede Utility Optimization
  3. Adherence Trumps Theoretical Perfection
  4. Spatio-Temporal Contextuality Defines Dietary Feasibility
  5. Macronutrient Partitioning & Glycemic Load Over Raw Calories
* **Q2. 3 Professional Controversies**:
  1. Keto/LCHF vs. DASH/Mediterranean in Metabolic Syndrome
  2. Clinical Validity of Smartwatch Calorie Estimates ($\alpha=0.65$ damping factor solution)
  3. Exploit vs. Explore/Push in Health Recommender Systems (Nudge Theory solution)
* **Q3. 10 In-depth Understanding Questions**:
  Multi-level reasoning across Why, What-if, Trade-off, Failure Case, Evidence, Comparison, Design Decision, and Real-World Scenarios.
