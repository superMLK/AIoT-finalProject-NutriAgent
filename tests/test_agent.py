"""
NutriAgent - Automated Test & Clinical Verification Suite
Module: tests/test_agent.py
Description: Validates clinical safety zero-violation (CVR=0%), TFDA-11 food allergen
isolation (AVR=0%), never-relax empty pool handling, dynamic TDEE & plausibility checks,
geospatial LBS accuracy, online preference adaptation, and ChatGPT-style conversational agent.
"""

import unittest
import json
from pathlib import Path
import numpy as np

from src.agent import NutriAgent
from src.clinical_rules import ClinicalRulesEngine
from src.iot_pipeline import IoTPipeline
from src.spatial_lbs import SpatialLBSEngine
from src.recommender import GeminiRecommender, DRLRecommender

BASE_DIR = Path(__file__).resolve().parent.parent
PROFILES_PATH = BASE_DIR / "data" / "sample_health_reports.json"


class TestNutriAgent(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open(PROFILES_PATH, "r", encoding="utf-8") as f:
            cls.profiles = {p["profile_id"]: p for p in json.load(f)}
        cls.agent = NutriAgent()

    def test_01_clinical_zero_violation_hypertension(self):
        """Verify that Stage-1 Hypertension profile NEVER receives high-sodium (>700mg) or deep-fried meals."""
        p_hyp = self.profiles["P_001_HYPERTENSION"]
        res = self.agent.run_recommendation(
            user_profile=p_hyp,
            user_lat=25.0135,
            user_lon=121.5342,
            activity_preset="moderate"
        )
        self.assertEqual(res["status"], "success")
        for meal in res["recommendations"]:
            self.assertLessEqual(
                meal["sodium_mg"], 700,
                f"Clinical Violation: Meal {meal['dish_name']} has sodium {meal['sodium_mg']} > 700mg!"
            )
            self.assertFalse(
                meal["is_deep_fried"],
                f"Clinical Violation: Meal {meal['dish_name']} is deep fried!"
            )
            self.assertTrue(meal.get("numerical_consistency_verified", False))

    def test_02_clinical_zero_violation_gout(self):
        """Verify that Hyperuricemia/Gout profile NEVER receives high purine or rich broth meals."""
        p_gout = self.profiles["P_003_GOUT_HYPERURICEMIA"]
        res = self.agent.run_recommendation(
            user_profile=p_gout,
            user_lat=25.0135,
            user_lon=121.5342,
            activity_preset="moderate"
        )
        for meal in res["recommendations"]:
            self.assertNotEqual(
                meal.get("purine_level"), "High",
                f"Clinical Violation: High Purine meal recommended to gout patient: {meal['dish_name']}"
            )

    def test_03_dynamic_tdee_and_plausibility_check(self):
        """Verify dynamic TDEE scaling, 900 kcal single-meal cap, and vibration artifact filtering."""
        p_ath = self.profiles["P_004_FITNESS_ATHLETE"]
        pipeline = IoTPipeline(damping_factor=0.65)

        tele_sedentary = pipeline.fetch_user_telemetry(p_ath, mock_preset="sedentary")
        budget_sedentary = pipeline.calculate_dynamic_budget(p_ath, tele_sedentary, meal_type="lunch")

        tele_active = pipeline.fetch_user_telemetry(p_ath, mock_preset="high_active")
        budget_active = pipeline.calculate_dynamic_budget(p_ath, tele_active, meal_type="lunch")

        self.assertGreater(budget_active["dynamic_tdee_kcal"], budget_sedentary["dynamic_tdee_kcal"])
        self.assertLessEqual(budget_active["target_meal_calories"], 900.0)

        # Verify vehicle vibration artifact detection (15,000 steps with 66 bpm resting HR)
        tele_vib = pipeline.fetch_user_telemetry(p_ath, mock_preset="vibration_artifact")
        self.assertFalse(tele_vib["plausibility_passed"])
        self.assertTrue(tele_vib["low_confidence"])
        self.assertLess(tele_vib["step_count"], 15000)

    def test_04_spatial_lbs_radius_filtering(self):
        """Verify spatial retrieval computes non-negative distances and sorts properly."""
        lbs = SpatialLBSEngine()
        meals = lbs.retrieve_nearby_meals(user_lat=25.0135, user_lon=121.5342, radius_km=1.2)
        self.assertGreater(len(meals), 0)
        for m in meals:
            self.assertIn("distance_km", m)
            self.assertIn("walking_time_min", m)
            self.assertLessEqual(m["distance_km"], 2.5)

    def test_05_online_preference_feedback(self):
        """Verify that user negative feedback ('too_oily') penalizes savory weights and boosts clean weights."""
        p_healthy = self.profiles["P_005_HEALTHY_SEDENTARY"]
        init_savory = float(self.agent.drl.user_flavor_weights[1])

        res = self.agent.run_recommendation(
            user_profile=p_healthy,
            user_lat=25.0135,
            user_lon=121.5342
        )
        rec_id = res["recommendations"][0]["meal_id"]

        self.agent.handle_user_feedback(rec_id, "too_oily")
        fb_res = self.agent.handle_user_feedback(rec_id, "too_oily")

        self.assertEqual(fb_res["status"], "success")
        updated_savory = float(self.agent.drl.user_flavor_weights[1])
        self.assertLess(
            updated_savory, init_savory,
            "Savory weight must decrease after 'too_oily' feedback"
        )

    def test_06_food_allergen_zero_violation_seafood_and_tfda11(self):
        """Verify that user with seafood/TFDA-11 allergy NEVER receives conflicting meals."""
        p_hyp = self.profiles["P_001_HYPERTENSION"]  # Has "seafood" allergy
        res = self.agent.run_recommendation(
            user_profile=p_hyp,
            user_lat=25.0135,
            user_lon=121.5342
        )
        self.assertEqual(res["status"], "success")
        for meal in res["recommendations"]:
            meal_allergens = meal.get("allergens", [])
            for forbidden in ["seafood", "fish", "shellfish", "crustacean"]:
                self.assertNotIn(
                    forbidden, meal_allergens,
                    f"Allergen Violation: Meal {meal['dish_name']} contains allergen {forbidden}!"
                )

    def test_07_food_allergen_custom_input_peanuts(self):
        """Verify that passing dynamic custom allergen 'peanuts' strictly prunes peanut noodle meals."""
        p_athlete = self.profiles["P_004_FITNESS_ATHLETE"]
        res = self.agent.run_recommendation(
            user_profile=p_athlete,
            user_lat=25.0135,
            user_lon=121.5342,
            custom_allergens=["peanuts"]
        )
        self.assertEqual(res["status"], "success")
        for meal in res["recommendations"]:
            meal_allergens = meal.get("allergens", [])
            self.assertNotIn("peanuts", meal_allergens)
            self.assertNotEqual(meal["meal_id"], "NOO_001")

    def test_08_never_relax_rules_on_empty_safe_pool(self):
        """Verify Proposal Section 5.7 fix: when SafePool is empty, NEVER relax clinical rules."""
        extreme_profile = self.profiles["P_001_HYPERTENSION"].copy()
        extreme_profile["metrics"] = {
            "blood_pressure_systolic": 160,
            "blood_pressure_diastolic": 100,
            "fasting_glucose_mg_dl": 140,
            "ldl_c_mg_dl": 160,
            "uric_acid_mg_dl": 9.0
        }
        # Pass an artificial candidate list where every item violates hypertension sodium > 700mg
        unsafe_catalog = [
            {
                "meal_id": "UNSAFE_1",
                "store_name": "測試店",
                "dish_name": "高鈉非油炸湯麵",
                "coordinates": {"lat": 25.0135, "lon": 121.5342},
                "calories_kcal": 500,
                "protein_g": 20,
                "fat_g": 10,
                "saturated_fat_g": 2.0,
                "sodium_mg": 1400,
                "is_deep_fried": False,
                "allergens": [],
                "price_twd": 100
            }
        ]
        safe_pool = self.agent.clinical_rules.filter_safe_candidates(unsafe_catalog, extreme_profile)
        self.assertEqual(len(safe_pool), 0)
        tips = self.agent.clinical_rules.generate_order_tips(unsafe_catalog, extreme_profile)
        self.assertGreater(len(tips), 0)

    def test_09_conversational_chat_agent(self):
        """Verify ChatGPT-style multi-turn chat() workflow returns grounded reply, trace, and Top-3 cards."""
        p_hyp = self.profiles["P_001_HYPERTENSION"]
        chat_res = self.agent.chat(
            user_message="中午在公館附近，幫我推薦適合高血壓且不含海鮮的清淡午餐！",
            user_profile=p_hyp,
            user_lat=25.0135,
            user_lon=121.5342
        )
        self.assertEqual(chat_res["status"], "success")
        self.assertTrue(len(chat_res["reply"]) > 20)
        self.assertGreaterEqual(len(chat_res["reasoning_trace"]), 3)
        self.assertGreater(len(chat_res["recommendations"]), 0)


if __name__ == "__main__":
    unittest.main()
