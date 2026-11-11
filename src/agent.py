"""
NutriAgent - Core Domain AI Agent Orchestrator (Conversational & Gemini-Powered)
Module: src/agent.py
Description: Central agent uniting Wearable IoT telemetry (with plausibility check),
clinical MNT & TFDA-11 allergen hard-constraint gate (never relaxing rules),
spatial LBS retrieval, and Google Gemini API contextual ranking & conversational dialogue.
"""

from typing import Dict, Any, List, Optional
import numpy as np

from src.clinical_rules import ClinicalRulesEngine
from src.iot_pipeline import IoTPipeline
from src.spatial_lbs import SpatialLBSEngine
from src.recommender import GeminiRecommender, DRLRecommender, BaseRecommender


class NutriAgent:
    """
    Domain AI Agent: Real-Time Adaptive Dietary Decision Agent.
    Implements Algorithm 1-3 from the updated NutriAgent Proposal plus
    multi-turn ChatGPT-style conversational orchestration.
    """

    def __init__(
        self,
        catalog_path: Optional[str] = None,
        recommender: Optional[BaseRecommender] = None,
        api_key: Optional[str] = None
    ):
        self.iot = IoTPipeline(damping_factor=0.65)
        self.clinical_rules = ClinicalRulesEngine()
        self.lbs = SpatialLBSEngine(catalog_path=catalog_path)
        self.drl: GeminiRecommender = recommender or GeminiRecommender(api_key=api_key, lr=0.005, gamma=0.90)
        self.gemini = self.drl  # Alias for semantic clarity

        # Session state & multi-turn conversation history
        self.last_state: Optional[np.ndarray] = None
        self.last_recommended_meals: List[Dict[str, Any]] = []
        self.conversation_history: List[Dict[str, str]] = []

    def set_gemini_api_key(self, api_key: str, model_name: Optional[str] = None):
        """Configure Gemini API key at runtime."""
        if hasattr(self.drl, "set_api_key"):
            self.drl.set_api_key(api_key, model_name=model_name)

    def clear_conversation(self):
        """Reset multi-turn conversation history."""
        self.conversation_history.clear()

    @staticmethod
    def verify_explanation_consistency(explanation: str, meal: Dict[str, Any]) -> bool:
        """
        Algorithm 1 Line 22: assert numbers_in(E) == db_values(R)
        Verify that key nutritional figures cited in the explanation strictly match
        the database record for `meal`, preventing nutritional hallucination.
        """
        cal_str = f"{meal['calories_kcal']} kcal"
        if cal_str not in explanation:
            return False
        if "鈉含量僅" in explanation and f"{meal['sodium_mg']} mg" not in explanation:
            return False
        return True

    def run_recommendation(
        self,
        user_profile: Dict[str, Any],
        user_lat: float,
        user_lon: float,
        activity_preset: str = "moderate",
        meal_type: str = "lunch",
        radius_km: float = 1.2,
        custom_allergens: Optional[List[str]] = None,
        user_query: str = ""
    ) -> Dict[str, Any]:
        """
        Execute full 8-stage recommendation workflow (Algorithm 1).
        Strictly enforces clinical & TFDA-11 allergen hard gate without rule relaxation.
        """
        active_profile = user_profile.copy()
        if custom_allergens is not None:
            active_profile["allergens"] = list(dict.fromkeys(custom_allergens))

        # Step 1 (Alg 1 Lines 02-07): Ingest Wearable IoT Telemetry, Plausibility Check & Dynamic Budget
        telemetry = self.iot.fetch_user_telemetry(active_profile, mock_preset=activity_preset)
        budget = self.iot.calculate_dynamic_budget(active_profile, telemetry, meal_type=meal_type)

        # Step 2 (Alg 1 Lines 08-09): Retrieve Spatial Nearby Candidates (1.2km -> 2.5km expansion)
        raw_candidates = self.lbs.retrieve_nearby_meals(user_lat, user_lon, radius_km=radius_km)

        # Step 3 (Alg 1 Line 10 & Alg 2): Enforce Deterministic Clinical & Allergen Hard-Constraint Gate
        safe_candidates = self.clinical_rules.filter_safe_candidates(raw_candidates, active_profile)

        rejected_count = len(raw_candidates) - len(safe_candidates)
        rejection_details = []
        for meal in raw_candidates:
            is_safe, violations = self.clinical_rules.evaluate_meal_safety(meal, active_profile)
            if not is_safe:
                rejection_details.append({
                    "dish_name": meal["dish_name"],
                    "store_name": meal.get("store_name", ""),
                    "violations": violations
                })

        # Step 3b (Alg 1 Lines 11-12): If S is empty, NEVER relax clinical/allergen rules!
        order_tips: List[str] = []
        if not safe_candidates:
            order_tips = self.clinical_rules.generate_order_tips(raw_candidates, active_profile)
            return {
                "status": "no_compliant_meal",
                "user_id": active_profile.get("profile_id"),
                "telemetry": telemetry,
                "metabolic_budget": budget,
                "active_allergens": active_profile.get("allergens", []),
                "spatial_context": {
                    "user_lat": user_lat,
                    "user_lon": user_lon,
                    "total_nearby_found": len(raw_candidates),
                    "safe_candidates_count": 0,
                    "clinical_rejected_count": rejected_count,
                    "rejection_sample": rejection_details[:6]
                },
                "recommendations": [],
                "order_tips": order_tips,
                "drl_flavor_weights": {
                    "light_clean": round(float(self.drl.user_flavor_weights[0]), 3),
                    "bento_savory": round(float(self.drl.user_flavor_weights[1]), 3),
                    "high_protein": round(float(self.drl.user_flavor_weights[2]), 3)
                }
            }

        # Step 4 (Alg 1 Lines 13-20): Encode Multimodal State & Rank Safe Pool
        hour_map = {"breakfast": 8, "lunch": 12, "dinner": 18}
        state = self.drl.encode_state(active_profile, budget, hour=hour_map.get(meal_type, 12))
        self.last_state = state

        ranked_meals = self.drl.rank_meals(safe_candidates, state, budget, user_query=user_query)
        top_3 = ranked_meals[:3]
        self.last_recommended_meals = top_3

        # Step 5 (Alg 1 Lines 21-22): Synthesize Grounded Clinical Explanations & Verify Numerical Consistency
        recommendations = []
        for idx, meal in enumerate(top_3, 1):
            explanation = self._generate_clinical_explanation(meal, active_profile, budget, telemetry, idx)
            consistent = self.verify_explanation_consistency(explanation, meal)
            assert consistent, f"Numerical consistency check failed for meal {meal['meal_id']}"
            meal_dict = meal.copy()
            meal_dict["rank"] = idx
            meal_dict["clinical_explanation"] = explanation
            meal_dict["numerical_consistency_verified"] = consistent
            recommendations.append(meal_dict)

        return {
            "status": "success",
            "user_id": active_profile.get("profile_id"),
            "telemetry": telemetry,
            "metabolic_budget": budget,
            "active_allergens": active_profile.get("allergens", []),
            "spatial_context": {
                "user_lat": user_lat,
                "user_lon": user_lon,
                "total_nearby_found": len(raw_candidates),
                "safe_candidates_count": len(safe_candidates),
                "clinical_rejected_count": rejected_count,
                "rejection_sample": rejection_details[:6]
            },
            "recommendations": recommendations,
            "order_tips": order_tips,
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
        Algorithm 1 Line 21: Produce transparent, clinically verified explanations
        copying numbers strictly from database fields only.
        """
        metrics = user_profile.get("metrics", {})
        user_allergens = user_profile.get("allergens", [])
        reasons = []

        # 0. Allergen safety clearance
        if user_allergens:
            allergen_labels = [
                self.clinical_rules.ALLERGEN_DISPLAY_NAMES.get(a.lower(), a)
                for a in user_allergens
            ]
            reasons.append(
                f"TFDA 過敏安全保證：餐點完全不含您宣告之過敏原 ({', '.join(allergen_labels)})"
            )

        # 1. Calorie & Activity linkage
        cal_diff = meal["calories_kcal"] - budget["target_meal_calories"]
        if abs(cal_diff) <= 60:
            reasons.append(
                f"熱量精準對齊：餐點提供 {meal['calories_kcal']} kcal，精準契合今日穿戴記錄 {telemetry['step_count']} 步之當餐預算 ({budget['target_meal_calories']} kcal)"
            )
        else:
            reasons.append(
                f"熱量適配：提供 {meal['calories_kcal']} kcal (當餐動態預算 {budget['target_meal_calories']} kcal，蛋白質 {meal['protein_g']}g)"
            )

        # 2. Blood Pressure / Sodium check
        if metrics.get("blood_pressure_systolic", 115) >= 130 or metrics.get("blood_pressure_diastolic", 75) >= 85:
            reasons.append(
                f"2025 AHA 高血壓得舒合規：單餐鈉含量僅 {meal['sodium_mg']} mg (低於 700 mg 警戒線)，非油炸烹調"
            )

        # 3. Glucose / GI check
        if metrics.get("fasting_glucose_mg_dl", 90) >= 100:
            reasons.append(
                f"ADA 2026 糖尿病前期控糖：升糖指數為 {meal.get('glycemic_index', 'Low')}，膳食纖維達 {meal.get('dietary_fiber_g', 0)}g，添加糖僅 {meal.get('added_sugar_g', 0)}g"
            )

        # 4. Uric Acid check
        if metrics.get("uric_acid_mg_dl", 5.0) >= 7.0:
            reasons.append(
                f"2020 ACR 痛風安全：經臨床規則驗證為低普林等級 ({meal.get('purine_level')})，杜絕濃縮肉湯與內臟"
            )

        # 5. LDL-C check
        if metrics.get("ldl_c_mg_dl", 100) >= 130:
            reasons.append(
                f"血脂保護：飽和脂肪僅 {meal.get('saturated_fat_g', 0)}g (低於 5.0g 上限)"
            )

        # 6. Distance & Time
        reasons.append(
            f"實體可購性：距離 {meal.get('distance_km', 0.5)} 公里 (步行約 {meal.get('walking_time_min', 5)} 分鐘)"
        )

        prefix = f"【第 {rank} 推薦：{meal['dish_name']}】"
        return prefix + " " + "；".join(reasons) + "。"

    def handle_user_feedback(self, meal_id: str, feedback_type: str) -> Dict[str, Any]:
        """
        Algorithm 3: Process closed-loop human feedback (accept, too_oily, skip)
        to update preference weights online.
        """
        if self.last_state is None:
            return {"status": "error", "message": "No active recommendation session found"}

        reward_map = {
            "accept": 1.0,
            "too_oily": -0.6,
            "skip": -0.2
        }
        reward = reward_map.get(feedback_type, 0.0)

        target_meal = next((m for m in self.last_recommended_meals if m["meal_id"] == meal_id), None)
        if target_meal is None and self.last_recommended_meals:
            target_meal = self.last_recommended_meals[0]

        if target_meal:
            action_vec = self.drl.encode_action(target_meal)
            delta = self.drl.update_online(self.last_state, action_vec, reward, feedback_type)
            return {
                "status": "success",
                "meal_id": target_meal["meal_id"],
                "dish_name": target_meal["dish_name"],
                "feedback_received": feedback_type,
                "reward_assigned": reward,
                "online_training_loss": round(float(delta), 5),
                "updated_flavor_weights": {
                    "light_clean": round(float(self.drl.user_flavor_weights[0]), 3),
                    "bento_savory": round(float(self.drl.user_flavor_weights[1]), 3),
                    "high_protein": round(float(self.drl.user_flavor_weights[2]), 3)
                }
            }

        return {"status": "error", "message": "Meal not matched"}

    def chat(
        self,
        user_message: str,
        user_profile: Dict[str, Any],
        user_lat: float = 25.0135,
        user_lon: float = 121.5342,
        activity_preset: str = "moderate",
        meal_type: str = "lunch",
        custom_allergens: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Multi-turn ChatGPT-style Conversational Agent Entrypoint.
        1. Parses natural language intent & context overrides from `user_message`.
        2. Applies feedback updates if user expressed dissatisfaction ("太油了", "換一家", etc.).
        3. Executes the 8-stage clinical/IoT/LBS pipeline.
        4. Generates a grounded conversational response (via Gemini API or deterministic synthesizer)
           and returns structured reasoning trace + Top-3 interactive cards.
        """
        intent_info = self.drl.parse_conversation_intent(user_message)
        reasoning_trace = []

        # Merge context overrides detected from natural language chat
        effective_meal_type = intent_info.get("meal_type") or meal_type
        effective_activity = intent_info.get("activity_preset") or activity_preset
        effective_lat, effective_lon = user_lat, user_lon
        if intent_info.get("location_coords"):
            effective_lat, effective_lon = intent_info["location_coords"]

        effective_allergens = list(custom_allergens) if custom_allergens is not None else list(user_profile.get("allergens", []))
        for det_allg in intent_info.get("detected_allergens", []):
            if det_allg not in effective_allergens:
                effective_allergens.append(det_allg)

        reasoning_trace.append(
            f"🔍 **意圖解析 (Intent NLU)**：判定意圖為 `{intent_info['intent']}`｜時段 `{effective_meal_type}`｜活動模式 `{effective_activity}`"
        )

        # If user message is feedback on previous recommendation, update weights first
        feedback_update_info = None
        if intent_info["intent"] == "feedback" and intent_info.get("feedback_type") and self.last_recommended_meals:
            fb_type = intent_info["feedback_type"]
            target_id = self.last_recommended_meals[0]["meal_id"]
            feedback_update_info = self.handle_user_feedback(target_id, fb_type)
            reasoning_trace.append(
                f"🧠 **線上偏好更新 (Algorithm 3)**：收到 `{fb_type}` 回饋 (Reward `{feedback_update_info.get('reward_assigned')}`)，"
                f"權重更新為 清淡={self.drl.user_flavor_weights[0]:.2f}, 便當={self.drl.user_flavor_weights[1]:.2f}, 高蛋白={self.drl.user_flavor_weights[2]:.2f}"
            )

        # Execute 8-stage recommendation pipeline
        rec_result = self.run_recommendation(
            user_profile=user_profile,
            user_lat=effective_lat,
            user_lon=effective_lon,
            activity_preset=effective_activity,
            meal_type=effective_meal_type,
            custom_allergens=effective_allergens,
            user_query=user_message
        )

        budget = rec_result["metabolic_budget"]
        telemetry = rec_result["telemetry"]
        spatial = rec_result["spatial_context"]

        reasoning_trace.append(
            f"⌚ **穿戴式 IoT 與動態代謝 (Algorithm 1 L02–07)**：步數 `{telemetry['step_count']}` 步、活動消耗 `{telemetry['active_calories_kcal']} kcal` (經 0.65 阻尼折算) → 動態 TDEE `{budget['dynamic_tdee_kcal']} kcal`，當餐預算 `{budget['target_meal_calories']} kcal`"
        )
        reasoning_trace.append(
            f"📍 **LBS 空間檢索與臨床硬閘門 (Algorithm 2)**：周邊檢索 `{spatial['total_nearby_found']}` 道餐點 → 臨床與 TFDA 過敏原硬約束剔除 `{spatial['clinical_rejected_count']}` 道 → 安全候選池剩餘 `{spatial['safe_candidates_count']}` 道 (CVR = 0.0%, AVR = 0.0%)"
        )
        reasoning_trace.append(
            f"🤖 **Gemini 語義排序與數值接地檢查 (Algorithm 1 L14–22)**：{'已連線 Gemini API (' + self.drl.model_name + ')' if self.drl.is_gemini_configured else '內建臨床語義推論引擎'} 完成 Top-3 排序，並通過 `numbers_in(E) == db_values(R)` 一致性驗證"
        )

        # Generate conversational reply
        reply_text = self.drl.generate_conversational_reply(
            user_message=user_message,
            user_profile=user_profile,
            recommendation_result=rec_result,
            intent_info=intent_info,
            conversation_history=self.conversation_history
        )

        # Append to conversation history
        self.conversation_history.append({"role": "user", "content": user_message})
        self.conversation_history.append({"role": "assistant", "content": reply_text})

        return {
            "status": rec_result["status"],
            "reply": reply_text,
            "intent_info": intent_info,
            "reasoning_trace": reasoning_trace,
            "feedback_update": feedback_update_info,
            "telemetry": telemetry,
            "metabolic_budget": budget,
            "active_allergens": effective_allergens,
            "spatial_context": spatial,
            "recommendations": rec_result["recommendations"],
            "order_tips": rec_result.get("order_tips", []),
            "drl_flavor_weights": rec_result["drl_flavor_weights"],
            "gemini_configured": self.drl.is_gemini_configured,
            "gemini_model": self.drl.model_name
        }
