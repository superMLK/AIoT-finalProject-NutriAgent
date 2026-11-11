# OpenSpec Technical Design: NutriAgent
Change ID: `proposal-nutriagent-v1`

## 1. System Architecture & Component Mapping

```
[User & Context] → [Multimodal Input] → [Planner Agent] → [Spatial LBS]
        ↓
[Clinical Hard-Constraint Gate] → [DRL Recommendation Engine] → [Explainable Decision] → [Web Cockpit & Feedback]
```

### Module Responsibilities:
1. `src/iot_pipeline.py`: Google Fit OAuth 2.0 client & synthetic circadian activity generator.
2. `src/clinical_rules.py`: Deterministic Medical Nutrition Therapy (MNT) constraint checker.
3. `src/spatial_lbs.py`: Spatial indexing (Haversine distance) and food database loader.
4. `src/recommender.py`: PyTorch Deep Q-Network (DQN) policy network and experience replay buffer.
5. `src/agent.py`: Central orchestrator uniting state encoding, hard filtering, scoring, and explanation.
6. `app.py`: Interactive demonstration web cockpit with spatial map rendering and telemetry dials.

---

## 2. Mathematical Formulations

### 2.1 Dynamic Caloric Budgeting
Given user weight $W$ (kg), height $H$ (cm), age $A$ (yr), and Google Fit cumulative active burn $C_{\text{act}}$:
$$\text{BMR} = 10 \cdot W + 6.25 \cdot H - 5 \cdot A + s \quad (s = +5 \text{ for male}, -161 \text{ for female})$$
$$\text{Dynamic TDEE} = \text{BMR} + \alpha \cdot C_{\text{act}} \quad (\alpha = 0.65 \text{ safety damping factor})$$
Meal Target for lunch/dinner:
$$\text{Target}_{\text{meal}} = \text{Dynamic TDEE} \times 0.35$$

### 2.2 Reinforcement Learning Formulation
* **State $s_t \in \mathbb{R}^8$**:
  $$s_t = \left[ \text{TimeOfDay}, \frac{\text{Target}_{\text{meal}}}{1000}, \frac{\text{Steps}}{10000}, \frac{\text{BP}_{\text{sys}}}{180}, \frac{\text{FG}}{200}, \text{Pref}_{\text{bento}}, \text{Pref}_{\text{light}}, \text{Pref}_{\text{noodle}} \right]$$
* **Action $a \in \mathcal{A}$**: Selection of a meal candidate $i$ from the filtered safe pool $\mathcal{S}_{\text{safe}}$.
* **Composite Scoring Function**:
  $$\text{Score}(s_t, a_i) = w_1 \cdot Q_\theta(s_t, a_i) + w_2 \cdot \text{NutriFit}(a_i, \mathbf{m}^*) - w_3 \cdot \text{Dist}(u, a_i)$$

---

## 3. Core Algorithm (Pseudocode)

```python
Algorithm 1: NutriAgent Real-Time Adaptive Dietary Decision Agent
Input : User Profile U, Health Metrics H, Location Loc, History D, Network Q_theta
Output: Top-3 Meal Recommendations TopRec, Clinical Explanations Exp

01: Initialize SafePool = EmptyList()
02: Initialize StateVector s_t = EmptyVector()
03: Try:
04:     FitTelemetry = GoogleFitAPI.FetchDailySummary(U.ID, Timestamp.Now())
05:     ActiveCalories = FitTelemetry.ActiveEnergyBurnedKcal
06:     Steps = FitTelemetry.StepCount
07: Catch APIException:
08:     ActiveCalories = BaselineActivityEstimate(U) # Fallback to default sedentary multiplier
09:     Steps = 0
10: BMR = CalculateHarrisBenedict(U.Gender, U.Weight, U.Height, U.Age)
11: DynamicTDEE = BMR + (ActiveCalories * 0.65) # Apply safety damping factor
12: CaloricBudget_Meal = AllocateMealBudget(DynamicTDEE, Timestamp.CurrentMealType())
13: MacroTargets = ComputeMacronutrientSplit(CaloricBudget_Meal, H)
14: RawCandidates = SpatialDatabase.QueryNearbyMeals(Loc.Lat, Loc.Lon, RadiusKm=1.0)
15: For Each Meal in RawCandidates:
16:     IsViolated = CheckClinicalRules(Meal, H) # DASH 限鈉 < 700mg, 控糖低 GI, 避普林
17:     If IsViolated == False:
18:         SafePool.Append(Meal)
19: s_t = EncodeState(U, H, Steps, ActiveCalories, CaloricBudget_Meal, Timestamp.Hour())
20: For Each Meal in SafePool:
21:     Q_val = Q_theta.Forward(s_t, Meal.NutritionalFlavorEmbedding)
22:     NutriFit = CosineSimilarity(Meal.Macronutrients, MacroTargets)
23:     Meal.TotalScore = (0.50 * Q_val) + (0.35 * NutriFit) - (0.15 * Meal.DistKm)
24: TopRec = SafePool.SortByDescending(TotalScore)[0:3]
25: Exp = GenerateClinicalExplanation(TopRec, H, FitTelemetry, MacroTargets)
26: Return TopRec, Exp
```
