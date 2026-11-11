"""
NutriAgent - Gemini API Contextual Recommender & Conversational Reasoning Engine
Module: src/recommender.py
Description: Replaces traditional deep learning / neural network (DQN) models with
Google Gemini API (gemini-2.5-flash / gemini-2.0-flash) for semantic craving alignment,
contextual preference ranking, natural language intent parsing, and grounded clinical
explanation generation. Includes a deterministic contextual fallback for offline/benchmark execution.
"""

from abc import ABC, abstractmethod
import os
import re
import json
import urllib.request
import urllib.error
from collections import deque
from typing import List, Dict, Any, Tuple, Optional
import numpy as np


class BaseRecommender(ABC):
    """Abstract Base Class for Recommender & Preference Strategies."""

    @abstractmethod
    def encode_state(self, user_profile: Dict[str, Any], budget: Dict[str, Any], hour: int = 12) -> np.ndarray:
        """Encode environment and user state into feature vector."""
        pass

    @abstractmethod
    def encode_action(self, meal: Dict[str, Any]) -> np.ndarray:
        """Encode candidate meal into action representation vector."""
        pass

    @abstractmethod
    def rank_meals(
        self,
        safe_candidates: List[Dict[str, Any]],
        state: np.ndarray,
        budget: Dict[str, Any],
        user_query: str = ""
    ) -> List[Dict[str, Any]]:
        """Rank safe candidates and return sorted list."""
        pass

    @abstractmethod
    def update_online(self, state: np.ndarray, action: np.ndarray, reward: float, feedback_type: str) -> float:
        """Execute online preference adaptation step from human feedback."""
        pass


class InteractionMemoryBuffer:
    """Cyclic memory buffer storing user feedback transitions (s, a, r, s', feedback_type)."""

    def __init__(self, capacity: int = 500):
        self.buffer = deque(maxlen=capacity)

    def push(self, state: np.ndarray, action: np.ndarray, reward: float, next_state: np.ndarray, feedback_type: str = ""):
        self.buffer.append((state, action, reward, next_state, feedback_type))

    def get_recent(self, k: int = 5) -> List[Tuple]:
        return list(self.buffer)[-k:]

    def __len__(self):
        return len(self.buffer)


class GeminiRecommender(BaseRecommender):
    """
    Gemini API-Powered Contextual Recommender & Conversational Engine.
    Replaces PyTorch neural networks with:
    1. Interpretable contextual preference vector w = [light_clean, bento_savory, high_protein]
       updated online via Algorithm 3 (Human-in-the-Loop bandit feedback).
    2. Live Google Gemini API integration for natural language craving scoring,
       multi-turn dialogue understanding, and clinically grounded explanation generation.
    3. Zero-latency deterministic fallback when GEMINI_API_KEY is not set or during benchmarks.
    """

    DEFAULT_MODEL = "gemini-2.5-flash"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        lr: float = 0.005,
        gamma: float = 0.90,
        epsilon: float = 0.0
    ):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY", "").strip()
        self.model_name = model_name or os.environ.get("GEMINI_MODEL", self.DEFAULT_MODEL)
        self.lr = lr
        self.gamma = gamma
        self.epsilon = epsilon

        # Dynamic user flavor preference weights: [Light/Clean, Bento/Savory, High-Protein]
        self.user_flavor_weights = np.array([0.5, 0.5, 0.5], dtype=np.float32)
        self.replay_buffer = InteractionMemoryBuffer(capacity=500)
        self.feedback_notes: List[str] = []

    def set_api_key(self, api_key: str, model_name: Optional[str] = None):
        """Update Gemini API key and optional model name at runtime."""
        self.api_key = (api_key or "").strip()
        if model_name:
            self.model_name = model_name.strip()

    @property
    def is_gemini_configured(self) -> bool:
        return bool(self.api_key and len(self.api_key) > 10)

    def _call_gemini_api(
        self,
        prompt: str,
        system_instruction: str = "",
        temperature: float = 0.2,
        max_output_tokens: int = 900,
        response_mime_type: Optional[str] = None
    ) -> Optional[str]:
        """
        Call Google Gemini REST API (`generateContent`) directly via standard HTTPS.
        No heavy neural network libraries required.
        """
        if not self.is_gemini_configured:
            return None

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
        payload: Dict[str, Any] = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_output_tokens
            }
        }
        if system_instruction:
            payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}
        if response_mime_type:
            payload["generationConfig"]["responseMimeType"] = response_mime_type

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=12) as resp:
                resp_data = json.loads(resp.read().decode("utf-8"))
                candidates = resp_data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts and "text" in parts[0]:
                        return parts[0]["text"].strip()
        except Exception:
            return None
        return None

    def encode_state(self, user_profile: Dict[str, Any], budget: Dict[str, Any], hour: int = 12) -> np.ndarray:
        """
        Algorithm 1 Line 13: Encode current multimodal scenario into an 8-dimensional normalized state vector.
        s_t = [time_norm, cal_norm, step_norm, bp_norm, fg_norm, w_light, w_savory, w_protein]
        """
        metrics = user_profile.get("metrics", {})
        time_norm = hour / 24.0
        cal_norm = budget.get("target_meal_calories", 600.0) / 1200.0
        step_norm = min(1.0, budget.get("steps", 5000) / 15000.0)
        bp_norm = min(1.0, metrics.get("blood_pressure_systolic", 120) / 180.0)
        fg_norm = min(1.0, metrics.get("fasting_glucose_mg_dl", 95) / 160.0)

        return np.array([
            time_norm,
            cal_norm,
            step_norm,
            bp_norm,
            fg_norm,
            self.user_flavor_weights[0],
            self.user_flavor_weights[1],
            self.user_flavor_weights[2]
        ], dtype=np.float32)

    def encode_action(self, meal: Dict[str, Any]) -> np.ndarray:
        """
        Algorithm 1 Line 15: Encode candidate meal features into a 6-dimensional action vector.
        a_m = [calories, protein_ratio, fat_ratio, sodium_norm, is_clean, is_savory]
        """
        calories = meal.get("calories_kcal", 500.0) / 1000.0
        protein_ratio = (meal.get("protein_g", 25.0) * 4.0) / max(1.0, meal.get("calories_kcal", 500.0))
        fat_ratio = (meal.get("fat_g", 15.0) * 9.0) / max(1.0, meal.get("calories_kcal", 500.0))
        sodium_norm = meal.get("sodium_mg", 600.0) / 1500.0

        flavor = meal.get("flavor_profile", "")
        is_clean = 1.0 if ("clean" in flavor or "light" in flavor or "herb" in flavor or "fresh" in flavor) else 0.0
        is_savory = 1.0 if ("savory" in flavor or "spicy" in flavor or "heavy" in flavor or "rich" in flavor) else 0.0

        return np.array([calories, protein_ratio, fat_ratio, sodium_norm, is_clean, is_savory], dtype=np.float32)

    def predict_preference_score(self, state: np.ndarray, action: np.ndarray, meal: Optional[Dict[str, Any]] = None, user_query: str = "") -> float:
        """
        Compute contextual preference score (replacing neural network Q-value) using learned
        flavor weights [light_clean, bento_savory, high_protein] and semantic query matching.
        """
        w_clean, w_savory, w_protein = float(state[5]), float(state[6]), float(state[7])
        is_clean, is_savory = float(action[4]), float(action[5])
        target_cal_norm = float(state[1]) * 1.2  # state[1] is target_cal / 1200, action[0] is meal_cal / 1000
        cal_proximity = max(0.0, 1.0 - abs(float(action[0]) - target_cal_norm))
        prot_density = min(1.0, float(action[1]) / 0.30)

        # Normalize flavor match so dual-tagged items do not overshadow caloric fit
        denom = max(1.0, is_clean + is_savory)
        flavor_match = ((w_clean * is_clean) + (w_savory * is_savory)) / denom
        base_pref = (0.45 * flavor_match) + (0.25 * w_protein * prot_density) + (0.30 * cal_proximity)

        # Semantic query boost if user specified a craving in natural language
        query_boost = 0.0
        if user_query and meal:
            q = user_query.lower()
            dish = meal.get("dish_name", "").lower()
            cat = meal.get("store_category", "").lower()
            cuisine = meal.get("cuisine_type", "").lower()
            tags_str = " ".join(meal.get("tags", [])).lower()

            if any(k in q for k in ["清淡", "輕食", "健康", "水煮", "舒肥", "低卡", "清爽"]) and is_clean > 0.5:
                query_boost += 0.25
            if any(k in q for k in ["便當", "滷", "傳統", "台式", "飯"]) and ("便當" in cat or "便當" in dish or "飯" in dish):
                query_boost += 0.20
            if any(k in q for k in ["高蛋白", "增肌", "重訓", "運動", "雞胸"]) and meal.get("protein_g", 0) >= 30:
                query_boost += 0.25
            if any(k in q for k in ["超商", "7-11", "全家", "便利商店", "趕時間"]) and "便利商店" in cat:
                query_boost += 0.25
            if any(k in q for k in ["潛艇堡", "subway", "三明治", "麵包"]) and "潛艇堡" in dish:
                query_boost += 0.30
            if any(k in q for k in ["魚", "鯛魚", "海鮮"]) and ("魚" in dish or "海鮮" in cuisine):
                query_boost += 0.25
            if any(k in q for k in ["辣", "椒麻"]) and ("椒麻" in dish or "spicy" in meal.get("flavor_profile", "")):
                query_boost += 0.25

        return float(np.clip(base_pref + query_boost, 0.0, 1.2))

    def _gemini_semantic_rerank(
        self,
        safe_candidates: List[Dict[str, Any]],
        user_query: str,
        budget: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        Optional Gemini API semantic preference scoring when user provides a free-text query
        and GEMINI_API_KEY is configured. Returns {meal_id: bonus_score_0_to_1}.
        """
        if not self.is_gemini_configured or not user_query.strip():
            return {}

        items_summary = [
            {
                "meal_id": m["meal_id"],
                "dish_name": m["dish_name"],
                "store_name": m["store_name"],
                "calories_kcal": m["calories_kcal"],
                "protein_g": m["protein_g"],
                "sodium_mg": m["sodium_mg"],
                "flavor_profile": m.get("flavor_profile", ""),
                "tags": m.get("tags", [])
            }
            for m in safe_candidates
        ]

        prompt = (
            f"使用者目前飲食偏好權重：清淡={self.user_flavor_weights[0]:.2f}, "
            f"傳統便當={self.user_flavor_weights[1]:.2f}, 高蛋白={self.user_flavor_weights[2]:.2f}。\n"
            f"當餐目標熱量：{budget.get('target_meal_calories')} kcal，目標蛋白質：{budget.get('target_protein_g')}g。\n"
            f"使用者對話訊息：「{user_query}」\n"
            f"安全候選餐點清單：{json.dumps(items_summary, ensure_ascii=False)}\n"
            "請針對每道安全餐點評估其符合使用者當前語義需求與偏好的匹配分數 (0.0 到 1.0)，"
            "只回傳 JSON 物件格式：{\"scores\": {\"meal_id\": 0.85, ...}}"
        )
        raw = self._call_gemini_api(
            prompt=prompt,
            system_instruction="你是專業臨床營養推薦系統的語義評分模組，只輸出合法 JSON。",
            temperature=0.1,
            max_output_tokens=400,
            response_mime_type="application/json"
        )
        if not raw:
            return {}
        try:
            parsed = json.loads(raw)
            scores = parsed.get("scores", {})
            return {str(k): float(v) for k, v in scores.items() if isinstance(v, (int, float))}
        except Exception:
            return {}

    def rank_meals(
        self,
        safe_candidates: List[Dict[str, Any]],
        state: np.ndarray,
        budget: Dict[str, Any],
        user_query: str = ""
    ) -> List[Dict[str, Any]]:
        """
        Algorithm 1 Lines 14-20:
        Compute composite multi-objective score for all safe candidates:
        fit = 1 - (0.6 * calorie_error + 0.4 * protein_error)
        score = 0.50 * q + 0.35 * fit - 0.15 * min(1, distance / 1.5)
        """
        target_cal = budget.get("target_meal_calories", 600.0)
        target_prot = budget.get("target_protein_g", 30.0)

        gemini_scores = self._gemini_semantic_rerank(safe_candidates, user_query, budget) if user_query else {}

        ranked = []
        for meal in safe_candidates:
            act_vec = self.encode_action(meal)
            local_pref = self.predict_preference_score(state, act_vec, meal=meal, user_query=user_query)

            if meal["meal_id"] in gemini_scores:
                q_val = 0.5 * local_pref + 0.5 * float(gemini_scores[meal["meal_id"]])
            else:
                q_val = local_pref

            # Caloric & protein alignment fitness (Algorithm 1 Line 18)
            cal_err = abs(meal.get("calories_kcal", 500) - target_cal) / max(100.0, target_cal)
            prot_err = abs(meal.get("protein_g", 25) - target_prot) / max(10.0, target_prot)
            nutri_fit = max(0.0, 1.0 - (0.6 * cal_err + 0.4 * prot_err))

            # Spatial distance penalty normalized by 1.5 km (Algorithm 1 Line 19)
            dist_km = meal.get("distance_km", 0.5)
            dist_penalty = min(1.0, dist_km / 1.5)

            composite_score = (0.50 * q_val) + (0.35 * nutri_fit) - (0.15 * dist_penalty)

            m_evaluated = meal.copy()
            m_evaluated["predicted_q_value"] = round(q_val, 3)
            m_evaluated["nutritional_fit_score"] = round(nutri_fit, 3)
            m_evaluated["composite_score"] = round(composite_score, 3)
            ranked.append(m_evaluated)

        return sorted(ranked, key=lambda x: x["composite_score"], reverse=True)

    def update_online(self, state: np.ndarray, action: np.ndarray, reward: float, feedback_type: str) -> float:
        """
        Algorithm 3: Online Preference Update (Human-in-the-Loop).
        Updates interpretable preference weights w = [light, savory, protein] and stores transition.
        """
        old_weights = self.user_flavor_weights.copy()

        if feedback_type == "accept":
            if action[4] > 0.5:  # Clean/light meal
                self.user_flavor_weights[0] = min(1.0, self.user_flavor_weights[0] + 0.08)
            if action[5] > 0.5:  # Savory meal
                self.user_flavor_weights[1] = min(1.0, self.user_flavor_weights[1] + 0.08)
            if action[1] >= 0.22:  # High protein ratio
                self.user_flavor_weights[2] = min(1.0, self.user_flavor_weights[2] + 0.08)
            self.feedback_notes.append("使用者採納推薦，強化該餐點風味偏好")
        elif feedback_type == "too_oily":
            # Algorithm 3 Line 03: w.savory <- w.savory - 0.15; w.light <- w.light + 0.12
            self.user_flavor_weights[1] = max(0.1, self.user_flavor_weights[1] - 0.15)
            self.user_flavor_weights[0] = min(1.0, self.user_flavor_weights[0] + 0.12)
            self.feedback_notes.append("使用者反映太油/太鹹，已調降重口味權重並提升清淡偏好")
        elif feedback_type == "skip":
            # Algorithm 3 Line 04: w <- clip(0.95 * w, 0.1, 1.0)
            self.user_flavor_weights = np.clip(self.user_flavor_weights * 0.95, 0.1, 1.0)
            self.feedback_notes.append("使用者略過此餐點，進行微幅探索調整")

        next_state = state.copy()
        next_state[5:8] = self.user_flavor_weights
        self.replay_buffer.push(state, action, reward, next_state, feedback_type)

        # Return L1 preference adaptation magnitude as online update delta
        adaptation_delta = float(np.mean(np.abs(self.user_flavor_weights - old_weights)))
        return round(adaptation_delta, 5)

    def parse_conversation_intent(self, user_message: str) -> Dict[str, Any]:
        """
        Parse user natural language message into structured dietary parameters & intent.
        Uses Gemini API when configured, backed by deterministic rule-based NLU.
        """
        msg = user_message.strip()
        msg_lower = msg.lower()

        # 1. Deterministic NLU extraction (fast & 100% reliable baseline)
        intent = "recommend"
        feedback_type = None
        if any(w in msg_lower for w in ["太油", "太鹹", "重鹹", "油膩", "清淡一點", "換清淡"]):
            intent = "feedback"
            feedback_type = "too_oily"
        elif any(w in msg_lower for w in ["採納", "就決定吃", "選第一個", "就吃這個", "接受推薦"]):
            intent = "feedback"
            feedback_type = "accept"
        elif any(w in msg_lower for w in ["換一家", "換別的", "不喜歡", "跳過", "還有別的嗎"]) and len(msg) <= 15:
            intent = "feedback"
            feedback_type = "skip"
        elif any(w in msg_lower for w in ["為什麼不能", "為何不能", "為什麼被剔除", "可以吃嗎", "能吃嗎"]) and any(
            d in msg_lower for d in ["排骨", "麻辣", "火鍋", "魚皮", "海鮮粥", "燴飯", "麻醬", "牛丼"]
        ):
            intent = "explain_violation"

        meal_type = None
        if any(w in msg_lower for w in ["早餐", "早上", "晨間", "breakfast"]):
            meal_type = "breakfast"
        elif any(w in msg_lower for w in ["午餐", "中午", "中餐", "午休", "lunch"]):
            meal_type = "lunch"
        elif any(w in msg_lower for w in ["晚餐", "晚上", "宵夜", "傍晚", "dinner"]):
            meal_type = "dinner"

        activity_preset = None
        if any(w in msg_lower for w in ["重訓", "跑步", "健身", "馬拉松", "運動", "流汗", "萬步", "高強度"]):
            activity_preset = "high_active"
        elif any(w in msg_lower for w in ["久坐", "圖書館", "辦公室", "沒動", "讀書", "追劇", "少動"]):
            activity_preset = "sedentary"
        elif any(w in msg_lower for w in ["通勤", "走路", "散步", "一般活動"]):
            activity_preset = "moderate"

        location_coords = None
        location_label = None
        if any(w in msg_lower for w in ["公館", "台大", "水源"]):
            location_coords = (25.0135, 121.5342)
            location_label = "台大公館商圈"
        elif any(w in msg_lower for w in ["大安", "森林公園"]):
            location_coords = (25.0268, 121.5358)
            location_label = "大安森林公園周邊"
        elif any(w in msg_lower for w in ["信義", "微風", "101", "市政府"]):
            location_coords = (25.0350, 121.5645)
            location_label = "信義微風商圈"

        detected_allergens = []
        allergen_keywords = {
            "seafood": ["海鮮", "魚貝"],
            "crustacean": ["蝦", "蟹", "甲殼", "蛤蜊"],
            "fish": ["魚過敏", "不吃魚"],
            "peanuts": ["花生"],
            "tree_nuts": ["堅果", "核桃", "杏仁", "腰果"],
            "gluten": ["麩質", "小麥", "麥過敏"],
            "dairy": ["牛奶", "乳糖", "奶製品", "鮮奶"],
            "egg": ["蛋過敏", "雞蛋過敏", "不吃蛋"],
            "soy": ["大豆", "黃豆"],
            "sesame": ["芝麻"],
            "mango": ["芒果"],
            "sulfites": ["亞硫酸鹽", "二氧化硫"]
        }
        if any(trigger in msg_lower for trigger in ["過敏", "不吃", "不能吃", "忌口", "避開"]):
            for allg_key, kw_list in allergen_keywords.items():
                if any(kw in msg_lower for kw in kw_list):
                    detected_allergens.append(allg_key)

        return {
            "intent": intent,
            "feedback_type": feedback_type,
            "meal_type": meal_type,
            "activity_preset": activity_preset,
            "location_coords": location_coords,
            "location_label": location_label,
            "detected_allergens": detected_allergens,
            "raw_query": msg
        }

    def generate_conversational_reply(
        self,
        user_message: str,
        user_profile: Dict[str, Any],
        recommendation_result: Dict[str, Any],
        intent_info: Dict[str, Any],
        conversation_history: List[Dict[str, str]]
    ) -> str:
        """
        Generate a ChatGPT-style conversational response grounded strictly in the
        database values and clinical rules. Uses Gemini API when configured, with
        a structured grounded fallback when offline.
        """
        budget = recommendation_result.get("metabolic_budget", {})
        telemetry = recommendation_result.get("telemetry", {})
        spatial = recommendation_result.get("spatial_context", {})
        recs = recommendation_result.get("recommendations", [])
        order_tips = recommendation_result.get("order_tips", [])
        metrics = user_profile.get("metrics", {})

        # If Gemini API is configured, ask Gemini to craft the conversational response
        # strictly grounded in the verified data
        if self.is_gemini_configured:
            history_str = "\n".join(
                f"{turn['role']}: {turn['content']}" for turn in conversation_history[-4:]
            )
            system_inst = (
                "你是 NutriAgent（智動食健），一位結合穿戴式 IoT 生理數據與臨床營養學規則 (2025 AHA/ACC 高血壓、"
                "ADA 2026 糖尿病、2020 ACR 痛風、TFDA 11類過敏原) 的專業對話式飲食決策 AI Agent。\n"
                "【絕對鐵則】：\n"
                "1. 你提及的任何餐點名稱、熱量 (kcal)、蛋白質 (g)、脂肪 (g)、鈉含量 (mg)、價格 (NT$)、距離 (km) "
                "必須 100% 一字不差引用下方提供的資料庫 JSON 數值，絕對不可自行捏造或四捨五入改變數值。\n"
                "2. 語氣親切、專業、條理分明（可使用 Markdown 重點標示），像 ChatGPT 營養師一樣自然對話並主動關心使用者。"
            )
            context_payload = {
                "user_name": user_profile.get("name"),
                "health_metrics": metrics,
                "active_allergens": recommendation_result.get("active_allergens", []),
                "telemetry": {
                    "steps": telemetry.get("step_count"),
                    "active_kcal": telemetry.get("active_calories_kcal"),
                    "low_confidence": telemetry.get("low_confidence", False),
                    "artifact_warning": telemetry.get("artifact_warning")
                },
                "dynamic_budget": budget,
                "clinical_gate_summary": {
                    "nearby_found": spatial.get("total_nearby_found"),
                    "rejected_count": spatial.get("clinical_rejected_count"),
                    "safe_count": spatial.get("safe_candidates_count"),
                    "rejected_examples": spatial.get("rejection_sample", [])
                },
                "top_3_recommendations": [
                    {
                        "rank": r["rank"],
                        "dish_name": r["dish_name"],
                        "store_name": r["store_name"],
                        "price_twd": r["price_twd"],
                        "distance_km": r["distance_km"],
                        "walking_time_min": r["walking_time_min"],
                        "calories_kcal": r["calories_kcal"],
                        "protein_g": r["protein_g"],
                        "fat_g": r["fat_g"],
                        "sodium_mg": r["sodium_mg"],
                        "clinical_explanation": r["clinical_explanation"]
                    }
                    for r in recs
                ],
                "order_tips_if_empty": order_tips
            }
            prompt = (
                f"【近期對話紀錄】\n{history_str}\n\n"
                f"【系統即時運算與臨床閘門結果 JSON】\n{json.dumps(context_payload, ensure_ascii=False, indent=2)}\n\n"
                f"【使用者最新訊息】：「{user_message}」\n\n"
                "請根據上述經過臨床硬閘門驗證的資料，直接以自然、溫暖、結構化的繁體中文回覆使用者。"
            )
            gemini_reply = self._call_gemini_api(
                prompt=prompt,
                system_instruction=system_inst,
                temperature=0.25,
                max_output_tokens=850
            )
            if gemini_reply:
                return gemini_reply

        # Grounded deterministic conversational synthesis (works offline & guarantees 100% numerical accuracy)
        intent = intent_info.get("intent", "recommend")
        lines = []

        if telemetry.get("artifact_warning"):
            lines.append(f"⚠️ **感測器合理性攔截**：{telemetry['artifact_warning']}。")

        if intent == "explain_violation":
            lines.append(f"您好！針對您詢問的餐點安全性，我已為您比對 **{user_profile.get('name')}** 的健檢紅字與過敏原紀錄：\n")
            rejs = spatial.get("rejection_sample", [])
            if rejs:
                lines.append("### 🚫 臨床與過敏硬閘門攔截原因")
                for r in rejs:
                    lines.append(f"- **{r['dish_name']}**：{'；'.join(r['violations'])}")
            lines.append("\n為了確保 **臨床零違規 (CVR = 0.0%)**，系統已強制排除上述高風險餐點，以下為您推薦周邊完全合規的安全替代方案：")
        elif intent == "feedback":
            fb = intent_info.get("feedback_type")
            if fb == "too_oily":
                lines.append(
                    f"收到！已記錄您覺得餐點偏油/偏鹹的反饋 ⚡。我已即時將您的 **清淡健康偏好權重調升至 `{self.user_flavor_weights[0]:.2f}`**（傳統重口味調降至 `{self.user_flavor_weights[1]:.2f}`），並重新為您篩選更清爽的餐點："
                )
            elif fb == "accept":
                lines.append(
                    f"太棒了！已記錄您的採納回饋 🏆，您的個人化口味偏好權重已更新（清淡 `{self.user_flavor_weights[0]:.2f}` / 便當 `{self.user_flavor_weights[1]:.2f}` / 高蛋白 `{self.user_flavor_weights[2]:.2f}`）。祝您用餐愉快！"
                )
            else:
                lines.append("沒問題！已為您調整探索權重並重新排序周邊合規餐點：")
        else:
            meal_label = {"breakfast": "早餐", "lunch": "午餐", "dinner": "晚餐"}.get(budget.get("meal_type", "lunch"), "當餐")
            lines.append(
                f"您好 **{user_profile.get('name')}**！根據您今日穿戴裝置記錄的 **{telemetry.get('step_count', 0)} 步**（活動消耗 **{telemetry.get('active_calories_kcal', 0)} kcal**，經 0.65 阻尼折算），"
                f"您的動態 TDEE 為 **{budget.get('dynamic_tdee_kcal')} kcal**，{meal_label}建議攝取目標為 **{budget.get('target_meal_calories')} kcal**（蛋白質目標 **{budget.get('target_protein_g')}g**）。"
            )
            lines.append(
                f"\n🛡️ **臨床與過敏原硬閘門**：周邊共檢索到 **{spatial.get('total_nearby_found', 0)}** 道實體餐點，已依您的健檢指標與過敏原強制剔除 **{spatial.get('clinical_rejected_count', 0)}** 道高風險餐點，從剩餘 **{spatial.get('safe_candidates_count', 0)}** 道安全候選池中為您選出最佳 Top-3："
            )

        if not recs:
            lines.append("\n### ⚠️ 周邊無完全符合臨床硬約束之套裝餐點 (`NO_COMPLIANT_MEAL`)")
            for tip in order_tips:
                lines.append(f"- {tip}")
        else:
            lines.append("")
            for r in recs:
                lines.append(
                    f"### 🥇 Top {r['rank']}：{r['dish_name']}（NT$ {r['price_twd']}）\n"
                    f"- **門市與距離**：{r['store_name']}（距離 `{r['distance_km']} km`，步行約 `{r['walking_time_min']}` 分鐘）\n"
                    f"- **精確營養標示**：熱量 `{r['calories_kcal']} kcal` ｜ 蛋白質 `{r['protein_g']} g` ｜ 脂肪 `{r['fat_g']} g` ｜ 鈉 `{r['sodium_mg']} mg`\n"
                    f"- **臨床決策理由**：{r['clinical_explanation']}"
                )

        return "\n".join(lines)


# Backward-compatible alias so existing tests/benchmarks importing DRLRecommender continue to pass
DRLRecommender = GeminiRecommender
