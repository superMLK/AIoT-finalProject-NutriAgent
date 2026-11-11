# OpenSpec Technical Design: AI Agent Continuity & Optimization Harness
Change ID: `agentic-continuity-optimization`

## 1. Architectural Strategy for Multi-Agent Collaboration

To allow AI agents to safely iterate, benchmark, and optimize without breaking existing clinical safety guarantees, the architecture is decoupled into three strict boundaries:

```
┌────────────────────────────────────────────────────────┐
│             AI Agent Workspace & Interfaces            │
│  [AGENTS.md Directives] ↔ [OpenSpec Changes & Specs]  │
└────────────────────────────────────────────────────────┘
                           │
       ┌───────────────────┴───────────────────┐
       ▼                                       ▼
┌─────────────────────────────┐   ┌──────────────────────────────┐
│  Safety Invariant Boundary   │   │  Optimization Target Zone    │
│  (Deterministic Gate)       │   │  (Safe for AI Modification)  │
│  • src/clinical_rules.py    │   │  • src/recommender.py (DRL)  │
│  • CVR = 0.0%, AVR = 0.0%   │   │  • src/iot_pipeline.py (IoT) │
│  • Zero-tolerance filtering │   │  • src/spatial_lbs.py (LBS)  │
└─────────────────────────────┘   └──────────────────────────────┘
                           │                       │
                           └───────────┬───────────┘
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │      Automated Verification Loops       │
                  │  • python -m unittest tests/test_agent  │
                  │  • python benchmark.py (JSON Metrics)   │
                  └─────────────────────────────────────────┘
```

---

## 2. Benchmark Metric Formulas

1. **Clinical Violation Rate (CVR)**:
   $$\text{CVR} = \frac{\sum_{i=1}^N \mathbb{I}(\text{Violation}_i)}{N} \times 100\% \quad (\text{Target: } 0.0\%)$$
2. **Allergen Violation Rate (AVR)**:
   $$\text{AVR} = \frac{\sum_{i=1}^N \mathbb{I}(\text{AllergenConflict}_i)}{N} \times 100\% \quad (\text{Target: } 0.0\%)$$
3. **Caloric Mean Absolute Error (MAE)**:
   $$\text{MAE}_{\text{cal}} = \frac{1}{N} \sum_{i=1}^N \lvert \text{Calories}_i - \text{TargetCalories}_i \rvert \quad (\text{Target: } \le 180\,\text{kcal})$$
4. **Latency Profile**:
   $$\text{Latency} = t_{\text{end}} - t_{\text{start}} \quad (\text{Target P95: } \le 50\,\text{ms})$$

---

## 3. Extensible Recommender Strategy Pattern
In `src/recommender.py`, AI agents can subclass `BaseRecommender` to implement alternate recommendation paradigms (e.g. Dueling DQN, Prioritized Experience Replay, Actor-Critic) without touching the orchestrator logic in `src/agent.py`.
