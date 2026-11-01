"""
NutriAgent - Spatial LBS & Restaurant Retrieval Engine
Module: src/spatial_lbs.py
Description: Performs geospatial indexing, Haversine distance calculations,
and candidate meal filtering within designated physical radius.
"""

import math
import json
from typing import List, Dict, Any, Tuple

class SpatialLBSEngine:
    """
    Location-Based Services (LBS) Engine for retrieving physical restaurants
    and convenience stores within physical walking distance.
    """

    # Pre-configured anchor districts in Taipei
    PRESET_LOCATIONS = {
        "ntu_gongguan": {"name": "台大公館商圈 (NTU Gongguan)", "lat": 25.0135, "lon": 121.5342},
        "daan_park": {"name": "大安森林公園周邊 (Daan District)", "lat": 25.0268, "lon": 121.5358},
        "xinyi_center": {"name": "信義商圈 (Xinyi Commercial Center)", "lat": 25.0350, "lon": 121.5645}
    }

    def __init__(self, catalog_path: str = "data/meal_catalog.json"):
        with open(catalog_path, "r", encoding="utf-8") as f:
            self.catalog = json.load(f)

    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate great-circle distance between two GPS coordinates in kilometers.
        """
        R = 6371.0  # Earth radius in kilometers
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = math.sin(delta_phi / 2.0) ** 2 + \
            math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return round(R * c, 3)

    def retrieve_nearby_meals(self, user_lat: float, user_lon: float, radius_km: float = 1.2) -> List[Dict[str, Any]]:
        """
        Retrieve all available meals within radius_km, augmenting each candidate
        with real-time physical distance and estimated walking time.
        """
        candidates = []
        for meal in self.catalog:
            coords = meal.get("coordinates", {})
            m_lat = coords.get("lat", user_lat)
            m_lon = coords.get("lon", user_lon)
            
            dist = self.haversine_distance(user_lat, user_lon, m_lat, m_lon)
            if dist <= radius_km:
                m_copy = meal.copy()
                m_copy["distance_km"] = dist
                m_copy["walking_time_min"] = max(1, int(round(dist * 12.0)))  # ~5 km/h walking speed
                candidates.append(m_copy)

        # Graceful degradation: if fewer than 4 candidates, expand search radius
        if len(candidates) < 4 and radius_km < 3.0:
            return self.retrieve_nearby_meals(user_lat, user_lon, radius_km=2.5)

        return sorted(candidates, key=lambda x: x["distance_km"])
