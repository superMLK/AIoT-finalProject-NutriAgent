"""
NutriAgent - Clinical Nutrition Rules & Allergen Isolation Engine
Module: src/clinical_rules.py
Description: Enforces medical nutrition therapy (MNT) hard-constraint pruning
(2025 AHA/ACC Hypertension, ADA 2026 Diabetes, 2020 ACR Gout, KDIGO CKD) and
zero-tolerance food allergen isolation aligned with Taiwan FDA (TFDA) 11 mandatory
allergen categories.
"""

from typing import Dict, Any, Tuple, List, Set


class ClinicalRulesEngine:
    """
    Deterministic Clinical Constraint Gate (Algorithm 2).
    Ensures zero clinical violations (CVR = 0.0%) and zero allergen exposure (AVR = 0.0%)
    before AI recommendation scoring. Never relaxes rules when safe pool is empty.
    """

    # TFDA 11 Mandatory Allergen Categories + Composite Aliases (e.g., seafood)
    ALLERGEN_ALIAS_MAP: Dict[str, Set[str]] = {
        # 1. 甲殼類 (Crustaceans)
        "crustacean": {"crustacean", "shellfish", "shrimp", "crab", "lobster", "prawn", "seafood", "甲殼類", "蝦", "蟹", "魚貝"},
        "shellfish": {"crustacean", "shellfish", "shrimp", "crab", "lobster", "prawn", "seafood", "甲殼類", "蝦", "蟹", "魚貝"},
        # 2. 芒果 (Mango)
        "mango": {"mango", "芒果"},
        # 3. 花生 (Peanuts)
        "peanuts": {"peanuts", "peanut", "nuts", "tree_nuts", "almond", "walnut", "花生", "堅果"},
        # 4. 牛奶/羊奶 (Milk & Dairy)
        "dairy": {"dairy", "milk", "goat_milk", "cheese", "butter", "lactose", "奶製品", "牛奶", "羊奶", "乳糖"},
        # 5. 蛋類 (Eggs)
        "egg": {"egg", "eggs", "蛋類", "雞蛋", "鴨蛋"},
        # 6. 堅果類 (Tree Nuts)
        "tree_nuts": {"tree_nuts", "nuts", "almond", "walnut", "cashew", "pistachio", "macadamia", "堅果", "堅果類", "杏仁", "核桃", "腰果"},
        # 7. 芝麻 (Sesame)
        "sesame": {"sesame", "芝麻"},
        # 8. 含麩質之穀物 (Gluten-containing Grains)
        "gluten": {"gluten", "wheat", "barley", "rye", "oats", "麩質", "小麥", "大麥", "黑麥", "燕麥"},
        # 9. 大豆 (Soybeans)
        "soy": {"soy", "soybean", "tofu", "edamame", "大豆", "黃豆", "黑豆", "毛豆"},
        # 10. 魚類 (Fish)
        "fish": {"fish", "salmon", "tilapia", "milkfish", "tuna", "cod", "seafood", "魚類", "魚", "鯛魚", "虱目魚", "鮭魚"},
        # 11. 亞硫酸鹽類 (Sulfites / Sulfur Dioxide >= 10 mg/kg)
        "sulfites": {"sulfites", "sulphites", "sulfur_dioxide", "so2", "亞硫酸鹽", "二氧化硫"},
        # Composite convenience key for backward compatibility (covers both Fish & Crustaceans/Molluscs)
        "seafood": {"seafood", "fish", "shellfish", "crustacean", "shrimp", "crab", "squid", "clam", "oyster", "海鮮", "魚貝", "魚類", "甲殼類"}
    }

    ALLERGEN_DISPLAY_NAMES: Dict[str, str] = {
        "crustacean": "甲殼類 (蝦/蟹)",
        "shellfish": "甲殼類/貝類",
        "mango": "芒果及其製品",
        "peanuts": "花生及其製品",
        "dairy": "牛奶/羊奶與乳製品",
        "egg": "蛋類及其製品",
        "tree_nuts": "堅果類 (杏仁/核桃/腰果)",
        "sesame": "芝麻及其製品",
        "gluten": "含麩質之穀物 (小麥/大麥)",
        "soy": "大豆/黃豆製品",
        "fish": "魚類及其製品",
        "sulfites": "亞硫酸鹽類",
        "seafood": "海鮮/魚貝甲殼類"
    }

    def __init__(self):
        # MNT threshold definitions according to 2025 AHA/ACC, ADA 2026, 2020 ACR, and TFDA Guidelines
        self.BP_SYSTOLIC_THRESHOLD = 130.0     # mmHg (2025 AHA/ACC Stage 1 Hypertension)
        self.BP_DIASTOLIC_THRESHOLD = 85.0     # mmHg
        self.FASTING_GLUCOSE_THRESHOLD = 100.0 # mg/dL (ADA 2026 Pre-diabetes / IFG)
        self.URIC_ACID_THRESHOLD = 7.0         # mg/dL (2020 ACR Hyperuricemia threshold)
        self.LDL_THRESHOLD = 130.0             # mg/dL (Elevated atherogenic LDL-C)
        self.EGFR_CKD_THRESHOLD = 60.0         # mL/min/1.73m^2 (CKD Stage 3+ K/P restriction)

    def check_allergen_conflict(self, meal_allergens: List[str], user_allergens: List[str]) -> Tuple[bool, List[str]]:
        """
        Check if candidate meal contains any food allergen declared by the user
        using TFDA 11-category alias expansion.
        """
        if not user_allergens or not meal_allergens:
            return False, []

        meal_allergen_set = {str(a).lower().strip() for a in meal_allergens}
        conflicts = []

        for u_all in user_allergens:
            u_clean = str(u_all).lower().strip()
            aliases = self.ALLERGEN_ALIAS_MAP.get(u_clean, {u_clean})
            if meal_allergen_set.intersection(aliases):
                display_name = self.ALLERGEN_DISPLAY_NAMES.get(u_clean, u_clean)
                if display_name not in conflicts:
                    conflicts.append(display_name)

        return len(conflicts) > 0, conflicts

    def evaluate_meal_safety(self, meal: Dict[str, Any], health_profile: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Algorithm 2: Clinical and Allergen Hard-Constraint Gate.
        Evaluate if a candidate meal is strictly safe for the user's clinical profile
        and declared food allergies.
        """
        violations = []
        metrics = health_profile.get("metrics", {})
        user_allergens = health_profile.get("allergens", [])

        # 0. Food Allergen Isolation (TFDA 11 Categories - Zero Tolerance)
        meal_allergens = meal.get("allergens", [])
        has_allergy, conflict_names = self.check_allergen_conflict(meal_allergens, user_allergens)
        if has_allergy:
            violations.append(
                f"違反 TFDA 食物過敏安全紅線: 餐點含有您過敏的食材 [{', '.join(conflict_names)}]"
            )

        # 1. Hypertension Rule (2025 AHA/ACC & DASH: restrict sodium <= 700mg/meal, prohibit deep-fried)
        bp_sys = metrics.get("blood_pressure_systolic", 115)
        bp_dia = metrics.get("blood_pressure_diastolic", 75)
        if bp_sys >= self.BP_SYSTOLIC_THRESHOLD or bp_dia >= self.BP_DIASTOLIC_THRESHOLD:
            if meal.get("sodium_mg", 0) > 700:
                violations.append(
                    f"違反 2025 AHA/ACC 高血壓得舒飲食限鈉標準: 單餐鈉含量 ({meal['sodium_mg']}mg) 超過安全上限 700mg"
                )
            if meal.get("is_deep_fried", False):
                violations.append("違反心血管保護指引: 嚴格禁止高飽和脂肪之深層油炸餐點")

        # 2. Pre-Diabetes / Insulin Resistance Rule (ADA 2026: restrict High GI & added sugar > 5g)
        glucose = metrics.get("fasting_glucose_mg_dl", 90)
        if glucose >= self.FASTING_GLUCOSE_THRESHOLD:
            if meal.get("glycemic_index") == "High":
                violations.append(
                    "違反 ADA 2026 糖尿病前期防護原則: 屬於高升糖指數 (High GI) 餐點，易引發餐後劇烈血糖震盪"
                )
            if meal.get("added_sugar_g", 0) > 5.0:
                violations.append(
                    f"違反控糖指引: 精緻添加糖 ({meal['added_sugar_g']}g) 超過單餐 5g 警戒線"
                )

        # 3. Hyperuricemia & Gout Rule (2020 ACR Guideline: eliminate High Purine & rich broths)
        uric_acid = metrics.get("uric_acid_mg_dl", 5.0)
        if uric_acid >= self.URIC_ACID_THRESHOLD:
            if meal.get("purine_level") == "High":
                violations.append(
                    "違反 2020 ACR 痛風防護紅線: 屬於高普林食材/長時間濃縮燉肉湯，具急性關節炎誘發風險"
                )

        # 4. Hyperlipidemia Rule (LDL-C >= 130 mg/dL: saturated fat <= 5g & non-fried)
        ldl = metrics.get("ldl_c_mg_dl", 100)
        if ldl >= self.LDL_THRESHOLD:
            if meal.get("saturated_fat_g", 0) > 5.0:
                violations.append(
                    f"違反降血脂標準: 飽和脂肪酸 ({meal['saturated_fat_g']}g) 超過安全上限 5.0g"
                )
            if meal.get("is_deep_fried", False) and "油炸" not in "".join(violations):
                violations.append("違反低密度膽固醇管理標準: 油炸烹調顯著加速動脈粥狀硬化")

        # 5. Chronic Kidney Disease (CKD Stage 3b-5: eGFR < 60 -> restrict High Potassium / Phosphorus)
        egfr = metrics.get("egfr_ml_min", 95.0)
        if egfr < self.EGFR_CKD_THRESHOLD:
            if meal.get("potassium_level") == "High" or meal.get("phosphorus_level") == "High":
                violations.append(
                    "違反慢性腎臟病 (CKD) 臨床指引: eGFR 偏低時嚴格限制高鉀/高磷食材，以防高血鉀症風險"
                )

        is_safe = len(violations) == 0
        return is_safe, violations

    def filter_safe_candidates(self, candidates: List[Dict[str, Any]], health_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filter out all clinically dangerous meals, returning only the Safe Candidate Pool S."""
        safe_pool = []
        for meal in candidates:
            is_safe, _ = self.evaluate_meal_safety(meal, health_profile)
            if is_safe:
                safe_pool.append(meal)
        return safe_pool

    def generate_order_tips(self, candidates: List[Dict[str, Any]], health_profile: Dict[str, Any]) -> List[str]:
        """
        Algorithm 1 Line 12: When SafePool S is empty, never relax clinical/allergen rules.
        Instead, return actionable clinical ordering adjustment tips (order_tips(C, H)).
        """
        metrics = health_profile.get("metrics", {})
        allergens = health_profile.get("allergens", [])
        tips = [
            "⚠️ 臨床安全守門提醒：周邊目前無完全符合您所有健檢紅字與過敏原限制的現成套裝餐點，系統堅持「不放寬醫療安全規則 (Zero Tolerance)」。"
        ]
        if allergens:
            names = [self.ALLERGEN_DISPLAY_NAMES.get(a.lower(), a) for a in allergens]
            tips.append(f"🛡️ 過敏原防護：點餐時請主動告知店家避開【{', '.join(names)}】及相關共用醬料（如沙茶醬、麻醬、海鮮高湯）。")
        if metrics.get("blood_pressure_systolic", 115) >= self.BP_SYSTOLIC_THRESHOLD:
            tips.append("🧂 控鈉調整建議：若於便當或小吃店點餐，請要求「不淋滷汁/醬汁減半、主菜去皮去炸粉、配菜過水瀝油」，或前往超商選購「無調味毛豆＋茶葉蛋＋無糖豆漿」組合。")
        if metrics.get("fasting_glucose_mg_dl", 90) >= self.FASTING_GLUCOSE_THRESHOLD:
            tips.append("🥗 控糖調整建議：請將白飯或麵條減半，優先攝取蛋白質與深色蔬菜（進食順序：水/菜 → 肉/蛋 → 飯）。")
        if metrics.get("uric_acid_mg_dl", 5.0) >= self.URIC_ACID_THRESHOLD:
            tips.append("🍲 痛風防護建議：請完全避開大骨濃湯、火鍋湯底與內臟類，改以白開水或無糖茶搭配清蒸蛋白質。")
        return tips
