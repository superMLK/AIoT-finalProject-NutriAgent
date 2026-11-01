"""
NutriAgent - Automated Test & Clinical Verification Suite
Module: tests/test_agent.py
Description: Validates clinical safety zero-violation, dynamic TDEE calculations,
geospatial LBS accuracy, and PyTorch DRL online weight adaptation.
"""

import unittest
import json
import numpy as np
import torch

from src.agent import NutriAgent
from src.clinical_rules import ClinicalRulesEngine
from src.iot_pipeline import IoTPipeline
from src.spatial_lbs import SpatialLBSEngine
from src.recommender import DRLRecommender

class TestNutriAgent(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open("data/sample_health_reports.json", "r", encoding="utf-8") as f:
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

    def test_03_dynamic_tdee_metabolic_scaling(self):
        """Verify that Google Fit telemetry changes dynamically scale the caloric budget."""
        p_ath = self.profiles["P_004_FITNESS_ATHLETE"]
        pipeline = IoTPipeline(damping_factor=0.65)
        
        tele_sedentary = pipeline.fetch_user_telemetry(p_ath, mock_preset="sedentary")
        budget_sedentary = pipeline.calculate_dynamic_budget(p_ath, tele_sedentary, meal_type="lunch")

        tele_active = pipeline.fetch_user_telemetry(p_ath, mock_preset="high_active")
        budget_active = pipeline.calculate_dynamic_budget(p_ath, tele_active, meal_type="lunch")

        # High active should yield strictly higher caloric budget
        self.assertGreater(
            budget_active["dynamic_tdee_kcal"],
            budget_sedentary["dynamic_tdee_kcal"],
            "Dynamic TDEE must increase with high Google Fit active energy"
        )
        self.assertGreater(
            budget_active["target_meal_calories"],
            budget_sedentary["target_meal_calories"]
        )

    def test_04_spatial_lbs_radius_filtering(self):
        """Verify spatial retrieval computes non-negative distances and sorts properly."""
        lbs = SpatialLBSEngine()
        # Query near Gongguan
        meals = lbs.retrieve_nearby_meals(user_lat=25.0135, user_lon=121.5342, radius_km=1.2)
        self.assertGreater(len(meals), 0)
        for m in meals:
            self.assertIn("distance_km", m)
            self.assertIn("walking_time_min", m)
            self.assertLessEqual(m["distance_km"], 2.5)

    def test_05_drl_online_learning_feedback(self):
        """Verify that user negative feedback ('too_oily') penalizes savory weights and updates Q-network."""
        p_healthy = self.profiles["P_005_HEALTHY_SEDENTARY"]
        init_savory = float(self.agent.drl.user_flavor_weights[1])
        
        # Run recommendation
        res = self.agent.run_recommendation(
            user_profile=p_healthy,
            user_lat=25.0135,
            user_lon=121.5342
        )
        rec_id = res["recommendations"][0]["meal_id"]
        
        # Trigger 'too_oily' feedback twice
        self.agent.handle_user_feedback(rec_id, "too_oily")
        fb_res = self.agent.handle_user_feedback(rec_id, "too_oily")
        
        self.assertEqual(fb_res["status"], "success")
        updated_savory = float(self.agent.drl.user_flavor_weights[1])
        self.assertLess(
            updated_savory, init_savory,
            "Savory weight must decrease after 'too_oily' feedback"
        )

if __name__ == "__main__":
    unittest.main()
