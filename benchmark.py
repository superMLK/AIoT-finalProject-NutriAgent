"""
NutriAgent - Objective Benchmark & Evaluation Harness for AI Agents
Module: benchmark.py
Description: Automated evaluation suite designed for AI Coding Agents and optimizers.
Calculates quantitative metrics across clinical safety, caloric precision,
inference latency, and DRL learning convergence, outputting machine-readable JSON.
"""

import sys
import io
import time
import json
from pathlib import Path
from typing import Dict, Any

# Ensure UTF-8 console output
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from src.agent import NutriAgent

def run_agent_benchmark() -> Dict[str, Any]:
    """
    Execute benchmark across all clinical cohorts and measure quantitative KPI scores.
    """
    base_dir = Path(__file__).resolve().parent
    profiles_path = base_dir / "data" / "sample_health_reports.json"
    with open(profiles_path, "r", encoding="utf-8") as f:
        profiles = json.load(f)

    agent = NutriAgent()
    total_recommendations = 0
    clinical_violations = 0
    allergen_violations = 0
    caloric_deviations = []
    latencies_ms = []

    test_scenarios = [
        {"preset": "sedentary", "meal": "breakfast"},
        {"preset": "moderate", "meal": "lunch"},
        {"preset": "high_active", "meal": "dinner"}
    ]

    print("=" * 70)
    print("🤖 NutriAgent AI Agent Optimization Benchmark Suite")
    print("=" * 70)
    print(f"評估母體：{len(profiles)} 組臨床病歷表型 × {len(test_scenarios)} 種物聯網生理情境...")

    for profile in profiles:
        for sc in test_scenarios:
            t_start = time.perf_counter()
            res = agent.run_recommendation(
                user_profile=profile,
                user_lat=25.0135,
                user_lon=121.5342,
                activity_preset=sc["preset"],
                meal_type=sc["meal"]
            )
            t_end = time.perf_counter()
            latencies_ms.append((t_end - t_start) * 1000.0)

            target_cal = res["metabolic_budget"]["target_meal_calories"]
            user_allergens = profile.get("allergens", [])

            for rec in res["recommendations"]:
                total_recommendations += 1
                # Check Caloric MAE
                caloric_deviations.append(abs(rec["calories_kcal"] - target_cal))

                # Check Clinical Violation (Hypertension BP >= 130 -> Sodium <= 700 & Non-Fried)
                bp = profile.get("metrics", {}).get("blood_pressure_systolic", 115)
                if bp >= 130 and (rec.get("sodium_mg", 0) > 700 or rec.get("is_deep_fried", False)):
                    clinical_violations += 1

                # Check Gout Violation (UA >= 7.0 -> No High Purine)
                ua = profile.get("metrics", {}).get("uric_acid_mg_dl", 5.0)
                if ua >= 7.0 and rec.get("purine_level") == "High":
                    clinical_violations += 1

                # Check Allergen Violation
                has_allergen_conflict, _ = agent.clinical_rules.check_allergen_conflict(
                    rec.get("allergens", []), user_allergens
                )
                if has_allergen_conflict:
                    allergen_violations += 1

    # Measure DRL Learning Adaptation Speed (Reward improvement over 10 feedback steps)
    init_savory = float(agent.drl.user_flavor_weights[1])
    sample_meal_id = "LSH_001"
    for _ in range(5):
        agent.handle_user_feedback(sample_meal_id, "too_oily")
    adapted_savory = float(agent.drl.user_flavor_weights[1])
    drl_adaptation_delta = round(init_savory - adapted_savory, 4)

    # Compute Aggregate Metrics
    cvr = (clinical_violations / max(1, total_recommendations)) * 100.0
    avr = (allergen_violations / max(1, total_recommendations)) * 100.0
    mean_cal_mae = sum(caloric_deviations) / max(1, len(caloric_deviations))
    mean_latency = sum(latencies_ms) / max(1, len(latencies_ms))
    p95_latency = sorted(latencies_ms)[int(len(latencies_ms) * 0.95)]

    benchmark_results = {
        "benchmark_status": "PASSED" if (cvr == 0.0 and avr == 0.0) else "FAILED",
        "total_evaluations": total_recommendations,
        "clinical_violation_rate_pct": round(cvr, 2),
        "allergen_violation_rate_pct": round(avr, 2),
        "caloric_mae_kcal": round(mean_cal_mae, 2),
        "mean_latency_ms": round(mean_latency, 2),
        "p95_latency_ms": round(p95_latency, 2),
        "drl_adaptation_sensitivity": drl_adaptation_delta,
        "kpi_targets": {
            "cvr_target_pct": 0.0,
            "avr_target_pct": 0.0,
            "caloric_mae_target_kcal": "<= 180.0",
            "latency_target_ms": "<= 50.0"
        }
    }

    print("\n" + "-" * 70)
    print("📊 基準評測量化結果 (Agent Benchmark Results):")
    print("-" * 70)
    print(f"  • 臨床禁忌違規率 (CVR): {benchmark_results['clinical_violation_rate_pct']}% (目標: 0.0%)")
    print(f"  • 食物過敏違規率 (AVR): {benchmark_results['allergen_violation_rate_pct']}% (目標: 0.0%)")
    print(f"  • 熱量目標平均偏差 (MAE): {benchmark_results['caloric_mae_kcal']} kcal")
    print(f"  • 平均推論耗時 (Mean Latency): {benchmark_results['mean_latency_ms']} ms")
    print(f"  • P95 推論耗時 (P95 Latency): {benchmark_results['p95_latency_ms']} ms")
    print(f"  • DRL 口味自適應靈敏度 (Sensitivity): {benchmark_results['drl_adaptation_sensitivity']}")
    print(f"  • 總體評測狀態: {'✅ 通過 (PASSED)' if benchmark_results['benchmark_status'] == 'PASSED' else '❌ 未通過 (FAILED)'}")
    print("=" * 70)

    # Machine-readable JSON output for automated agent consumption
    print("\n[AGENT_JSON_OUTPUT_START]")
    print(json.dumps(benchmark_results, indent=2))
    print("[AGENT_JSON_OUTPUT_END]\n")

    return benchmark_results

if __name__ == "__main__":
    run_agent_benchmark()
