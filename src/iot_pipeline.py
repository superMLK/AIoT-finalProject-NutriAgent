"""
NutriAgent - Wearable IoT & Metabolic Energy Pipeline
Module: src/iot_pipeline.py
Description: Ingests Google Fit REST API telemetry (or generates realistic circadian
sensor streams) and calculates dynamic real-time energy & macronutrient budgets.
"""

from typing import Dict, Any
from datetime import datetime

class IoTPipeline:
    """
    Connects to Google Fit REST API or simulates wearable telemetry
    to calculate real-time metabolic deficit.
    """

    def __init__(self, damping_factor: float = 0.65):
        # Damping factor prevents smartwatch calorie overestimation from causing overeating
        self.damping_factor = damping_factor

    def fetch_user_telemetry(self, user_profile: Dict[str, Any], mock_preset: str = "moderate") -> Dict[str, Any]:
        """
        Fetch real-time activity metrics. In production, this calls Google Fit API.
        For standalone evaluation, it generates parameterized telemetry based on preset.
        """
        presets = {
            "sedentary": {
                "step_count": 1850,
                "active_calories_kcal": 110,
                "heart_rate_avg_bpm": 68,
                "activity_duration_min": 15,
                "status_label": "久坐少動 (Sedentary / Desk Work)"
            },
            "moderate": {
                "step_count": 6800,
                "active_calories_kcal": 320,
                "heart_rate_avg_bpm": 78,
                "activity_duration_min": 55,
                "status_label": "一般通勤步行 (Moderate Active)"
            },
            "high_active": {
                "step_count": 14200,
                "active_calories_kcal": 680,
                "heart_rate_avg_bpm": 115,
                "activity_duration_min": 110,
                "status_label": "高強度運動/訓練 (High Athletic Training)"
            }
        }
        telemetry = presets.get(mock_preset, presets["moderate"]).copy()
        telemetry["timestamp"] = datetime.now().isoformat()
        return telemetry

    def calculate_bmr(self, gender: str, weight_kg: float, height_cm: float, age: int) -> float:
        """Calculate Basal Metabolic Rate using Mifflin-St Jeor / Harris-Benedict formula."""
        if gender.lower() == "male":
            return (10.0 * weight_kg) + (6.25 * height_cm) - (5.0 * age) + 5.0
        else:
            return (10.0 * weight_kg) + (6.25 * height_cm) - (5.0 * age) - 161.0

    def calculate_dynamic_budget(self, user_profile: Dict[str, Any], telemetry: Dict[str, Any], meal_type: str = "lunch") -> Dict[str, Any]:
        """
        Compute real-time dynamic TDEE and target calories/macros for the designated meal.
        """
        gender = user_profile.get("gender", "male")
        weight = float(user_profile.get("weight_kg", 70.0))
        height = float(user_profile.get("height_cm", 172.0))
        age = int(user_profile.get("age", 30))

        bmr = self.calculate_bmr(gender, weight, height, age)
        active_kcal = float(telemetry.get("active_calories_kcal", 200.0))
        
        # Dynamic TDEE with safety damping
        dynamic_tdee = bmr + (active_kcal * self.damping_factor)

        # Meal allocation ratios
        meal_ratios = {
            "breakfast": 0.25,
            "lunch": 0.40,
            "dinner": 0.35
        }
        ratio = meal_ratios.get(meal_type.lower(), 0.35)
        target_meal_calories = round(dynamic_tdee * ratio, 1)

        # Determine target macronutrients based on health conditions
        clinical_conditions = user_profile.get("clinical_conditions", [])
        
        if "Athletic_Hyperactive" in clinical_conditions:
            # 40% Carb, 35% Protein, 25% Fat
            carb_ratio, prot_ratio, fat_ratio = 0.40, 0.35, 0.25
        elif "Pre_Diabetes" in clinical_conditions or "Insulin_Resistance" in clinical_conditions:
            # Low carb focus: 35% Carb, 35% Protein, 30% Fat
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
            "target_meal_calories": target_meal_calories,
            "target_carb_g": target_carb_g,
            "target_protein_g": target_protein_g,
            "target_fat_g": target_fat_g,
            "meal_type": meal_type,
            "steps": telemetry.get("step_count", 0),
            "active_calories_kcal": active_kcal
        }
