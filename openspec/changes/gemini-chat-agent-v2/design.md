# Technical Design: Gemini API Integration & Conversational Agent Architecture

## 1. Architecture Flow (Updated)
$$\text{User Natural Language / Context} \rightarrow \text{IoT Adapter & Plausibility Check} \rightarrow \text{Dynamic TDEE (Cap 900 kcal)} \rightarrow \text{Spatial LBS (1.2km/2.5km)} \rightarrow \text{Deterministic Clinical & TFDA-11 Allergen Gate} \rightarrow \text{Gemini API Contextual Ranking & Grounded Dialogue} \rightarrow \text{ChatGPT-Style Interactive UI}$$

## 2. Key Technical Decisions
1. **Zero Clinical Regression with Gemini API Grounding**:
   - The deterministic gate (`ClinicalRulesEngine`) executes *before* Gemini API ranking or response generation.
   - Gemini only ranks and explains meals inside the verified `SafePool`.
   - Every response passes through `verify_numerical_consistency()` so nutrition numbers strictly match `meal_catalog.json`.
2. **Dual-Mode Gemini Client (`GeminiRecommender`)**:
   - Uses standard HTTPS REST calls (`https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent`) or `google-genai` when `GEMINI_API_KEY` is configured via environment variable or UI sidebar.
   - Falls back cleanly to a deterministic contextual preference model when offline or during high-speed benchmark evaluation (`< 5 ms` latency).
3. **Never-Relax Safety Invariant**:
   - If `SafePool` is empty, `NutriAgent` returns `status = "no_compliant_meal"` with empty `recommendations` and actionable `order_tips` rather than relaxing clinical rules.
