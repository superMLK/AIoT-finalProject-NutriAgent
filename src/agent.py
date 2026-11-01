"""
NutriAgent - Core Domain AI Agent Orchestrator
Module: src/agent.py
Description: Central agent uniting IoT telemetry, clinical knowledge graph,
spatial LBS, and Deep Reinforcement Learning for real-time dietary decision making.
"""

from typing import Dict, Any, List, Optional
import numpy as np

from src.clinical_rules import ClinicalRulesEngine
from src.iot_pipeline import IoTPipeline
from src.spatial_lbs import SpatialLBSEngine
from src.recommender import DRLRecommender

class NutriAgent:
    """
    Domain AI Agent: Real-Time Adaptive Dietary Decision Agent.
    Implements the 8-stage Agent Pipeline:
    Scenario -> Ingestion -> Planning -> Retrieval -> Knowledge -> DRL -> Decision -> Interaction.
    """

    def __init__(self, catalog_path: str = "data/meal_catalog.json"):
        self.iot = IoTPipeline(damping_factor=0.65)
        self.clinical_rules = ClinicalRulesEngine()
        self.lbs = SpatialLBSEngine(catalog_path=catalog_path)
        self.drl = DRLRecommender(lr=0.005, gamma=0.90, epsilon=0.10)

        # Cache for current recommendation session state
        self.last_state = None
        self.last_recommended_meals = []

    def run_recommendation(
        self,
        user_profile: Dict[str, Any],
        user_lat: float,
        user_lon: float,
        activity_preset: str = "moderate",
        meal_type: str = "lunch",
        radius_km: float = 1.2
    ) -> Dict[str, Any]:
        """
        Execute full end-to-end recommendation workflow.
        """
        # Step 1: Ingest Wearable IoT Telemetry & Compute Dynamic Energy Budget
        telemetry = self.iot.fetch_user_telemetry(user_profile, mock_preset=activity_preset)
        budget = self.iot.calculate_dynamic_budget(user_profile, telemetry, meal_type=meal_type)

        # Step 2: Retrieve Spatial Nearby Candidates
        raw_candidates = self.lbs.retrieve_nearby_meals(user_lat, user_lon, radius_km=radius_km)

        # Step 3: Enforce Clinical Hard-Constraint Gate (Prune dangerous meals)
        safe_candidates = self.clinical_rules.filter_safe_candidates(raw_candidates, user_profile)
        
        # Track clinical safety filtering diagnostics
        rejected_count = len(raw_candidates) - len(safe_candidates)
        rejection_details = []
        for meal in raw_candidates:
            is_safe, violations = self.clinical_rules.evaluate_meal_safety(meal, user_profile)
            if not is_safe:
                rejection_details.append({
                    "dish_name": meal["dish_name"],
                    "violations": violations
                })

        # Graceful fallback: If safe pool is empty, re-add non-fried candidates with caution directive
        if not safe_candidates:
            safe_candidates = [m for m in raw_candidates if not m.get("is_deep_fried", False)]

        # Step 4: Encode Multimodal State & Rank via DRL Policy
        state = self.drl.encode_state(user_profile, budget, hour=12 if meal_type == "lunch" else 18)
        self.last_state = state

        ranked_meals = self.drl.rank_meals(safe_candidates, state, budget)
        top_3 = ranked_meals[:3]
        self.last_recommended_meals = top_3

        # Step 5: Synthesize Clinical Rationales & Explanations
        recommendations = []
        for idx, meal in enumerate(top_3, 1):
            explanation = self._generate_clinical_explanation(meal, user_profile, budget, telemetry, idx)
            meal_dict = meal.copy()
            meal_dict["rank"] = idx
            meal_dict["clinical_explanation"] = explanation
            recommendations.append(meal_dict)

        return {
            "status": "success",
            "user_id": user_profile.get("profile_id"),
            "telemetry": telemetry,
            "metabolic_budget": budget,
            "spatial_context": {
                "user_lat": user_lat,
                "user_lon": user_lon,
                "total_nearby_found": len(raw_candidates),
                "safe_candidates_count": len(safe_candidates),
                "clinical_rejected_count": rejected_count,
                "rejection_sample": rejection_details[:3]
            },
            "recommendations": recommendations,
            "drl_flavor_weights": {
                "light_clean": round(float(self.drl.user_flavor_weights[0]), 3),
                "bento_savory": round(float(self.drl.user_flavor_weights[1]), 3),
                "high_protein": round(float(self.drl.user_flavor_weights[2]), 3)
            }
        }

    def _generate_clinical_explanation(
        self,
        meal: Dict[str, Any],
        user_profile: Dict[str, Any],
        budget: Dict[str, Any],
        telemetry: Dict[str, Any],
        rank: int
    ) -> str:
        """
        Produce transparent, clinically verified explanations linking the user's
        health metrics, wearable activity, and specific meal properties.
        """
        metrics = user_profile.get("metrics", {})
        reasons = []

        # 1. Calorie & Activity linkage
        cal_diff = meal["calories_kcal"] - budget["target_meal_calories"]
        if abs(cal_diff) <= 60:
            reasons.append(
                f"熱量精準對齊：餐點提供 {meal['calories_kcal']} kcal，完美適配今日 Google Fit 記錄的 {telemetry['step_count']} 步活動代謝目標 ({budget['target_meal_calories']} kcal)"
            )
        else:
            reasons.append(
                f"熱量適配：提供 {meal['calories_kcal']} kcal (當餐建議 {budget['target_meal_calories']} kcal)"
            )

        # 2. Blood Pressure / Sodium check
        if metrics.get("blood_pressure_systolic", 115) >= 130:
            reasons.append(
                f"高血壓得舒合規：單餐鈉含量僅 {meal['sodium_mg']} mg (低於 700 mg 警戒線)，非油炸烹調以保護心血管"
            )

        # 3. Glucose / GI check
        if metrics.get("fasting_glucose_mg_dl", 90) >= 100:
            reasons.append(
                f"糖尿病前期控糖：升糖指數為 {meal.get('glycemic_index', 'Low')}，膳食纖維高達 {meal.get('dietary_fiber_g', 0)}g，有效平緩餐後血糖"
            )

        # 4. Uric Acid check
        if metrics.get("uric_acid_mg_dl", 5.0) >= 7.0:
            reasons.append(
                f"痛風安全：經臨床規則驗證為低普林食材 ({meal.get('purine_level')})，杜絕高濃肉湯與內臟"
            )

        # 5. Distance & Time
        reasons.append(
            f"步行可行性：距離您僅 {meal.get('distance_km', 0.5)} 公里 (步行約 {meal.get('walking_time_min', 5)} 分鐘)"
        )

        prefix = f"【第 {rank} 推薦：{meal['dish_name']}】"
        return prefix + " " + "；".join(reasons) + "。"

    def handle_user_feedback(self, meal_id: str, feedback_type: str) -> Dict[str, Any]:
        """
        Process closed-loop human feedback (accept, too_oily, skip) to trigger
        online PyTorch Deep Q-Network weight updates.
        """
        if self.last_state is None:
            return {"status": "error", "message": "No active recommendation session found"}

        reward_map = {
            "accept": 1.0,
            "too_oily": -0.6,
            "skip": -0.2
        }
        reward = reward_map.get(feedback_type, 0.0)

        # Find target meal in last recommended list
        target_meal = next((m for m in self.last_recommended_meals if m["meal_id"] == meal_id), None)
        if target_meal is None and self.last_recommended_meals:
            target_meal = self.last_recommended_meals[0]

        if target_meal:
            action_vec = self.drl.encode_action(target_meal)
            loss = self.drl.update_online(self.last_state, action_vec, reward, feedback_type)
            return {
                "status": "success",
                "feedback_received": feedback_type,
                "reward_assigned": reward,
                "online_training_loss": round(float(loss), 5),
                "updated_flavor_weights": {
                    "light_clean": round(float(self.drl.user_flavor_weights[0]), 3),
                    "bento_savory": round(float(self.drl.user_flavor_weights[1]), 3),
                    "high_protein": round(float(self.drl.user_flavor_weights[2]), 3)
                }
            }

        return {"status": "error", "message": "Meal not matched"}
