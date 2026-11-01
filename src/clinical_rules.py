"""
NutriAgent - Clinical Nutrition Rules Engine
Module: src/clinical_rules.py
Description: Enforces medical nutrition therapy (MNT) hard-constraint pruning
based on clinical checkup metrics (Blood Pressure, Glucose, Uric Acid, Lipids).
"""

from typing import Dict, Any, Tuple, List

class ClinicalRulesEngine:
    """
    Deterministic Clinical Constraint Gate.
    Ensures zero clinical violations (CVR = 0.0%) before AI recommendation.
    """

    def __init__(self):
        # MNT threshold definitions according to AHA, ADA, and Taiwan Health Guidelines
        self.BP_SYSTOLIC_THRESHOLD = 130.0   # mmHg (Stage 1 Hypertension border)
        self.BP_DIASTOLIC_THRESHOLD = 85.0   # mmHg
        self.FASTING_GLUCOSE_THRESHOLD = 100.0 # mg/dL (Pre-diabetes / Impaired Fasting Glucose)
        self.URIC_ACID_THRESHOLD = 7.0       # mg/dL (Hyperuricemia threshold)
        self.LDL_THRESHOLD = 130.0           # mg/dL (Elevated atherogenic lipoprotein)

    def evaluate_meal_safety(self, meal: Dict[str, Any], health_profile: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Evaluate if a candidate meal is strictly safe for the user's clinical profile.
        Returns:
            is_safe (bool): True if all medical rules pass, False if any violation occurs.
            violations (list of str): Explanations of violated clinical boundaries.
        """
        violations = []
        metrics = health_profile.get("metrics", {})
        
        bp_sys = metrics.get("blood_pressure_systolic", 115)
        bp_dia = metrics.get("blood_pressure_diastolic", 75)
        glucose = metrics.get("fasting_glucose_mg_dl", 90)
        uric_acid = metrics.get("uric_acid_mg_dl", 5.0)
        ldl = metrics.get("ldl_c_mg_dl", 100)

        # 1. Hypertension Rule (DASH Diet Standard: restrict sodium < 700mg per meal, avoid deep-fried)
        if bp_sys >= self.BP_SYSTOLIC_THRESHOLD or bp_dia >= self.BP_DIASTOLIC_THRESHOLD:
            if meal.get("sodium_mg", 0) > 700:
                violations.append(
                    f"違反高血壓得舒飲食限鈉標準: 單餐鈉含量 ({meal['sodium_mg']}mg) 超過安全上限 700mg"
                )
            if meal.get("is_deep_fried", False):
                violations.append("違反心血管保護指引: 嚴格禁止高飽和脂肪之深層油炸餐點")

        # 2. Pre-Diabetes / Insulin Resistance Rule (ADA Guidelines: restrict High GI & added sugar)
        if glucose >= self.FASTING_GLUCOSE_THRESHOLD:
            if meal.get("glycemic_index") == "High":
                violations.append(
                    "違反糖尿病前期防護原則: 屬於高升糖指數 (High GI) 餐點，易引發餐後劇烈血糖震盪"
                )
            if meal.get("added_sugar_g", 0) > 5.0:
                violations.append(
                    f"違反控糖指引: 精緻添加糖 ({meal['added_sugar_g']}g) 超過單餐 5g 警戒線"
                )

        # 3. Hyperuricemia & Gout Rule (Rheumatology Guidelines: eliminate High Purine & rich broths)
        if uric_acid >= self.URIC_ACID_THRESHOLD:
            if meal.get("purine_level") == "High":
                violations.append(
                    "違反痛風防護紅線: 屬於高普林食材/長時間濃縮燉肉湯，具急性關節炎誘發風險"
                )

        # 4. Hyperlipidemia Rule (Cardiovascular guidelines: saturated fat < 5g)
        if ldl >= self.LDL_THRESHOLD:
            if meal.get("saturated_fat_g", 0) > 5.0:
                violations.append(
                    f"違反降血脂標準: 飽和脂肪酸 ({meal['saturated_fat_g']}g) 超過安全上限 5.0g"
                )
            if meal.get("is_deep_fried", False) and "油炸" not in "".join(violations):
                violations.append("違反低密度膽固醇管理標準: 油炸烹調顯著加速動脈粥狀硬化")

        is_safe = len(violations) == 0
        return is_safe, violations

    def filter_safe_candidates(self, candidates: List[Dict[str, Any]], health_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filter out all clinically dangerous meals, returning only the Safe Candidate Pool."""
        safe_pool = []
        for meal in candidates:
            is_safe, violations = self.evaluate_meal_safety(meal, health_profile)
            if is_safe:
                safe_pool.append(meal)
        return safe_pool
