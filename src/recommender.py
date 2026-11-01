"""
NutriAgent - Deep Reinforcement Learning Recommender Engine
Module: src/recommender.py
Description: PyTorch-based Deep Q-Network (DQN) policy model with dynamic
experience replay for real-time personalization and preference adaptation.
"""

import random
from collections import deque
from typing import List, Dict, Any, Tuple
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

class NutriQNetwork(nn.Module):
    """
    Deep Q-Network for Dietary Action Value Estimation.
    Input: Concatenation of State Vector (dim=8) and Action Meal Vector (dim=6).
    Output: Scalar predicted Q-value Q(s, a).
    """

    def __init__(self, input_dim: int = 14, hidden_dim: int = 32):
        super(NutriQNetwork, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.LeakyReLU(0.1),
            nn.Linear(hidden_dim, hidden_dim),
            nn.LeakyReLU(0.1),
            nn.Linear(hidden_dim, 1)
        )

    def forward(self, state_action_vec: torch.Tensor) -> torch.Tensor:
        return self.net(state_action_vec)


class ExperienceReplayBuffer:
    """Cyclic buffer for storing agent transitions (s, a, r, s')."""

    def __init__(self, capacity: int = 500):
        self.buffer = deque(maxlen=capacity)

    def push(self, state: np.ndarray, action: np.ndarray, reward: float, next_state: np.ndarray):
        self.buffer.append((state, action, reward, next_state))

    def sample(self, batch_size: int = 16) -> List[Tuple]:
        return random.sample(self.buffer, min(batch_size, len(self.buffer)))

    def __len__(self):
        return len(self.buffer)


class DRLRecommender:
    """
    Reinforcement Learning Agent orchestrating DQN inference,
    multi-objective ranking, and online parameter optimization.
    """

    def __init__(self, lr: float = 0.005, gamma: float = 0.90, epsilon: float = 0.15):
        self.gamma = gamma
        self.epsilon = epsilon
        self.device = torch.device("cpu")

        self.model = NutriQNetwork(input_dim=14, hidden_dim=32).to(self.device)
        self.optimizer = optim.Adam(self.model.parameters(), lr=lr)
        self.loss_fn = nn.SmoothL1Loss()  # Huber loss for robust Q-learning
        self.replay_buffer = ExperienceReplayBuffer(capacity=500)

        # Dynamic user flavor preference weights [Light/Clean, Bento/Savory, High-Protein]
        self.user_flavor_weights = np.array([0.5, 0.5, 0.5], dtype=np.float32)

    def encode_state(self, user_profile: Dict[str, Any], budget: Dict[str, Any], hour: int = 12) -> np.ndarray:
        """
        Encode current multimodal scenario into an 8-dimensional normalized state vector.
        """
        metrics = user_profile.get("metrics", {})
        time_norm = hour / 24.0
        cal_norm = budget.get("target_meal_calories", 600.0) / 1200.0
        step_norm = min(1.0, budget.get("steps", 5000) / 15000.0)
        bp_norm = min(1.0, metrics.get("blood_pressure_systolic", 120) / 180.0)
        fg_norm = min(1.0, metrics.get("fasting_glucose_mg_dl", 95) / 160.0)

        # Append current user flavor preferences
        state = np.array([
            time_norm,
            cal_norm,
            step_norm,
            bp_norm,
            fg_norm,
            self.user_flavor_weights[0],
            self.user_flavor_weights[1],
            self.user_flavor_weights[2]
        ], dtype=np.float32)
        return state

    def encode_action(self, meal: Dict[str, Any]) -> np.ndarray:
        """
        Encode candidate meal features into a 6-dimensional action vector.
        """
        calories = meal.get("calories_kcal", 500.0) / 1000.0
        protein_ratio = (meal.get("protein_g", 25.0) * 4.0) / max(1.0, meal.get("calories_kcal", 500.0))
        fat_ratio = (meal.get("fat_g", 15.0) * 9.0) / max(1.0, meal.get("calories_kcal", 500.0))
        sodium_norm = meal.get("sodium_mg", 600.0) / 1500.0

        # Flavor indicator (Clean vs Savory)
        flavor = meal.get("flavor_profile", "")
        is_clean = 1.0 if "clean" in flavor or "light" in flavor or "herb" in flavor else 0.0
        is_savory = 1.0 if "savory" in flavor or "spicy" in flavor else 0.0

        return np.array([calories, protein_ratio, fat_ratio, sodium_norm, is_clean, is_savory], dtype=np.float32)

    def predict_q_value(self, state: np.ndarray, action: np.ndarray) -> float:
        """Predict expected Q-value for a specific state-action pair."""
        sa_vec = torch.from_numpy(np.concatenate([state, action])).float().unsqueeze(0).to(self.device)
        self.model.eval()
        with torch.no_grad():
            q_val = self.model(sa_vec).item()
        return float(q_val)

    def rank_meals(self, safe_candidates: List[Dict[str, Any]], state: np.ndarray, budget: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Compute composite multi-objective score for all safe candidates.
        Composite Score = 0.50 * Q_value + 0.35 * NutritionalFit - 0.15 * DistancePenalty
        """
        target_cal = budget.get("target_meal_calories", 600.0)
        target_prot = budget.get("target_protein_g", 30.0)

        ranked = []
        for meal in safe_candidates:
            act_vec = self.encode_action(meal)
            q_val = self.predict_q_value(state, act_vec)

            # Epsilon-greedy exploration nudge
            if random.random() < self.epsilon:
                q_val += random.uniform(-0.15, 0.15)

            # Caloric & protein alignment fitness
            cal_err = abs(meal.get("calories_kcal", 500) - target_cal) / max(100.0, target_cal)
            prot_err = abs(meal.get("protein_g", 25) - target_prot) / max(10.0, target_prot)
            nutri_fit = max(0.0, 1.0 - (0.6 * cal_err + 0.4 * prot_err))

            # Spatial distance penalty (normalized by 1.5 km)
            dist_km = meal.get("distance_km", 0.5)
            dist_penalty = min(1.0, dist_km / 1.5)

            # Multi-objective composite score
            composite_score = (0.50 * q_val) + (0.35 * nutri_fit) - (0.15 * dist_penalty)

            m_evaluated = meal.copy()
            m_evaluated["predicted_q_value"] = round(q_val, 3)
            m_evaluated["nutritional_fit_score"] = round(nutri_fit, 3)
            m_evaluated["composite_score"] = round(composite_score, 3)
            ranked.append(m_evaluated)

        return sorted(ranked, key=lambda x: x["composite_score"], reverse=True)

    def update_online(self, state: np.ndarray, action: np.ndarray, reward: float, feedback_type: str):
        """
        Perform online Q-learning parameter update and update flavor preference weights.
        """
        # 1. Update internal flavor weights
        if feedback_type == "accept":
            # Strengthen chosen action attributes
            if action[4] > 0.5:  # Clean meal
                self.user_flavor_weights[0] = min(1.0, self.user_flavor_weights[0] + 0.08)
            if action[5] > 0.5:  # Savory meal
                self.user_flavor_weights[1] = min(1.0, self.user_flavor_weights[1] + 0.08)
        elif feedback_type == "too_oily":
            # Penalize savory, boost clean/light
            self.user_flavor_weights[1] = max(0.1, self.user_flavor_weights[1] - 0.15)
            self.user_flavor_weights[0] = min(1.0, self.user_flavor_weights[0] + 0.12)
        elif feedback_type == "skip":
            # Mild exploration penalty
            self.user_flavor_weights = np.clip(self.user_flavor_weights * 0.95, 0.1, 1.0)

        # 2. Store in replay buffer
        next_state = state.copy()
        next_state[5:8] = self.user_flavor_weights
        self.replay_buffer.push(state, action, reward, next_state)

        # 3. Mini-batch gradient step
        if len(self.replay_buffer) >= 2:
            batch = self.replay_buffer.sample(batch_size=8)
            self.model.train()
            self.optimizer.zero_grad()

            loss = torch.tensor(0.0, device=self.device)
            for s, a, r, s_next in batch:
                sa = torch.from_numpy(np.concatenate([s, a])).float().unsqueeze(0).to(self.device)
                pred_q = self.model(sa)
                target_q = torch.tensor([[r]], dtype=torch.float32, device=self.device)
                loss = loss + self.loss_fn(pred_q, target_q)

            loss = loss / len(batch)
            loss.backward()
            self.optimizer.step()
            return float(loss.item())
        return 0.0
