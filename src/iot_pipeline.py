"""
NutriAgent - Wearable IoT Adapter & Metabolic Energy Pipeline
Module: src/iot_pipeline.py
Description: Implements Algorithm 1 Lines 02-07 from the updated NutriAgent Proposal:
- Wearable IoT Adapter (Android Health Connect / Apple HealthKit / Simulator)
- Timeout/failure fallback with LOW_CONF flag
- Cross-sensor plausibility check (steps vs. heart rate to filter vehicle vibration artifacts)
- Mifflin-St Jeor BMR + 0.65 damped activity calories + 900 kcal single-meal cap
"""

from typing import Dict, Any
from datetime import datetime


class IoTPipeline:
    """
    IoT Adapter and Dynamic Metabolic Budget Calculator.
    Note: Google Fit REST API is deprecated in 2026; this adapter abstracts
    Android Health Connect / Apple HealthKit streams and provides a calibrated simulator.
    """

    SINGLE_MEAL_MAX_CAP_KCAL = 900.0  # Algorithm 1 Line 07: Physiological single-meal absorption cap

    def __init__(self, damping_factor: float = 0.65):
        # Damping factor (0.65) mitigates wearable energy expenditure MAPE (>30%)
        self.damping_factor = damping_factor

    def static_estimate(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Algorithm 1 Line 03: Fallback static estimate when wearable stream times out or is denied.
        Flags LOW_CONF (low_confidence = True) without interrupting pipeline execution.
        """
        return {
            "step_count": 3000,
            "active_calories_kcal": 150,
            "heart_rate_avg_bpm": 72,
            "activity_duration_min": 20,
            "status_label": "靜態備援估計 (Wearable Offline / Static Estimate)",
            "source": "static_fallback",
            "low_confidence": True,
            "plausibility_passed": True,
            "timestamp": datetime.now().isoformat()
        }

    def plausibility_check(self, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Algorithm 1 Line 04: Cross-sensor plausibility check (steps vs. heart rate).
        Detects vehicle vibration artifacts (e.g., >10,000 steps while heart rate stays at resting <=70 bpm).
        """
        checked = telemetry.copy()
        steps = int(checked.get("step_count", 0))
        hr = float(checked.get("heart_rate_avg_bpm", 75))
        duration = max(1, int(checked.get("activity_duration_min", 30)))
        step_rate = steps / duration  # steps per active minute

        # If high step volume/cadence occurs with resting heart rate (<= 70 bpm), flag artifact
        if steps > 10000 and hr <= 70.0:
            checked["plausibility_passed"] = False
            checked["artifact_warning"] = "偵測到步數激增但心率維持靜止 (疑似行車震動偽訊號)，已自動校正活動熱量"
            checked["raw_step_count"] = steps
            checked["step_count"] = 2500
            checked["active_calories_kcal"] = min(float(checked.get("active_calories_kcal", 120)), 140.0)
            checked["low_confidence"] = True
        else:
            checked.setdefault("plausibility_passed", True)
            checked.setdefault("low_confidence", False)

        return checked

    def fetch_user_telemetry(self, user_profile: Dict[str, Any], mock_preset: str = "moderate") -> Dict[str, Any]:
        """
        Algorithm 1 Lines 02-04: Fetch wearable telemetry via IoTAdapter, handle fallback,
        and run cross-sensor plausibility verification.
        """
        presets = {
            "sedentary": {
                "step_count": 1850,
                "active_calories_kcal": 110,
                "heart_rate_avg_bpm": 68,
                "activity_duration_min": 15,
                "status_label": "久坐少動 (Sedentary / Desk Work)",
                "source": "health_connect_simulator"
            },
            "moderate": {
                "step_count": 6800,
                "active_calories_kcal": 320,
                "heart_rate_avg_bpm": 78,
                "activity_duration_min": 55,
                "status_label": "一般通勤步行 (Moderate Active)",
                "source": "health_connect_simulator"
            },
            "high_active": {
                "step_count": 14200,
                "active_calories_kcal": 680,
                "heart_rate_avg_bpm": 115,
                "activity_duration_min": 110,
                "status_label": "高強度運動/訓練 (High Athletic Training)",
                "source": "health_connect_simulator"
            },
            "vibration_artifact": {
                "step_count": 15000,
                "active_calories_kcal": 720,
                "heart_rate_avg_bpm": 66,
                "activity_duration_min": 60,
                "status_label": "異常震動測試 (Vehicle Vibration Artifact)",
                "source": "health_connect_simulator"
            }
        }

        if mock_preset == "offline_timeout":
            return self.static_estimate(user_profile)

        telemetry = presets.get(mock_preset, presets["moderate"]).copy()
        telemetry["timestamp"] = datetime.now().isoformat()
        telemetry["low_confidence"] = False
        return self.plausibility_check(telemetry)

    def calculate_bmr(self, gender: str, weight_kg: float, height_cm: float, age: int) -> float:
        """Algorithm 1 Line 05: Calculate Basal Metabolic Rate using Mifflin-St Jeor formula [22]."""
        if gender.lower() == "male":
            return (10.0 * weight_kg) + (6.25 * height_cm) - (5.0 * age) + 5.0
        else:
            return (10.0 * weight_kg) + (6.25 * height_cm) - (5.0 * age) - 161.0

    def calculate_dynamic_budget(
        self,
        user_profile: Dict[str, Any],
        telemetry: Dict[str, Any],
        meal_type: str = "lunch"
    ) -> Dict[str, Any]:
        """
        Algorithm 1 Lines 05-07:
        BMR <- MifflinStJeor(U.sex, U.weight, U.height, U.age)
        TDEE <- BMR + 0.65 * telemetry.active_kcal
        budget <- min(TDEE * ratio[t], 900); macros <- split(budget, H)
        """
        gender = user_profile.get("gender", "male")
        weight = float(user_profile.get("weight_kg", 70.0))
        height = float(user_profile.get("height_cm", 172.0))
        age = int(user_profile.get("age", 30))

        bmr = self.calculate_bmr(gender, weight, height, age)
        active_kcal = float(telemetry.get("active_calories_kcal", 200.0))

        # Dynamic TDEE with 0.65 safety damping factor
        dynamic_tdee = bmr + (active_kcal * self.damping_factor)

        # Meal allocation ratios
        meal_ratios = {
            "breakfast": 0.25,
            "lunch": 0.40,
            "dinner": 0.35
        }
        ratio = meal_ratios.get(meal_type.lower(), 0.35)
        raw_meal_calories = dynamic_tdee * ratio
        capped = raw_meal_calories > self.SINGLE_MEAL_MAX_CAP_KCAL
        target_meal_calories = round(min(raw_meal_calories, self.SINGLE_MEAL_MAX_CAP_KCAL), 1)

        # Determine target macronutrients based on clinical conditions & metrics
        clinical_conditions = user_profile.get("clinical_conditions", [])
        metrics = user_profile.get("metrics", {})
        fg = metrics.get("fasting_glucose_mg_dl", 90)

        if "Athletic_Hyperactive" in clinical_conditions:
            # 40% Carb, 35% Protein, 25% Fat
            carb_ratio, prot_ratio, fat_ratio = 0.40, 0.35, 0.25
        elif "Pre_Diabetes" in clinical_conditions or "Insulin_Resistance" in clinical_conditions or fg >= 100:
            # ADA 2026 mild low-carb pattern: 35% Carb, 35% Protein, 30% Fat
            carb_ratio, prot_ratio, fat_ratio = 0.35, 0.35, 0.30
        else:
            # Balanced DASH standard: 50% Carb, 25% Protein, 25% Fat
            carb_ratio, prot_ratio, fat_ratio = 0.50, 0.25, 0.25

        target_carb_g = round((target_meal_calories * carb_ratio) / 4.0, 1)
        target_protein_g = round((target_meal_calories * prot_ratio) / 4.0, 1)
        target_fat_g = round((target_meal_calories * fat_ratio) / 9.0, 1)

        return {
            "bmr_kcal": round(bmr, 1),
            "dynamic_tdee_kcal": round(dynamic_tdee, 1),
            "raw_meal_calories": round(raw_meal_calories, 1),
            "single_meal_cap_applied": capped,
            "target_meal_calories": target_meal_calories,
            "target_carb_g": target_carb_g,
            "target_protein_g": target_protein_g,
            "target_fat_g": target_fat_g,
            "meal_type": meal_type,
            "steps": telemetry.get("step_count", 0),
            "active_calories_kcal": active_kcal,
            "low_confidence": telemetry.get("low_confidence", False)
        }
