"""
NutriAgent - Command Line End-to-End Execution & Conversational Agent Demonstration
Module: demo_run.py
Description: Executes a complete run of the updated NutriAgent pipeline:
1. Ingests User Health Profile & TFDA-11 Declared Allergens
2. Ingests Wearable IoT Telemetry (with Plausibility Check) & Computes Dynamic TDEE (with 900 kcal cap)
3. Retrieves Nearby Physical Restaurants (LBS 1.2km -> 2.5km)
4. Enforces Deterministic Clinical Hard-Constraints & Allergen Gate (never relaxing rules)
5. Performs Gemini API Contextual Preference Ranking & Numerical Consistency Verification
6. Demonstrates Multi-Turn ChatGPT-style Conversational Interaction & Online Feedback Update
"""

import sys
import io
import json
from pathlib import Path

# Force UTF-8 encoding for standard output on Windows
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from src.agent import NutriAgent


def main():
    print("=" * 75)
    print("🥗 NutriAgent 智動食健 - 結合穿戴式 IoT、臨床營養規則與 Gemini 對談式代理人")
    print("=" * 75)

    # 1. Initialize Agent
    agent = NutriAgent()

    # 2. Load User Profile
    base_dir = Path(__file__).resolve().parent
    profiles_path = base_dir / "data" / "sample_health_reports.json"
    with open(profiles_path, "r", encoding="utf-8") as f:
        profiles = {p["profile_id"]: p for p in json.load(f)}

    user = profiles["P_001_HYPERTENSION"]
    print(f"\n[步驟 1] 載入使用者健檢報告與 TFDA 過敏原宣告：")
    print(f"  • 姓名：{user['name']}")
    print(f"  • 生理特徵：{user['gender']}, {user['age']}歲, {user['height_cm']}cm, {user['weight_kg']}kg (BMI: {user['metrics']['bmi']})")
    print(f"  • 健檢指標：收縮壓 {user['metrics']['blood_pressure_systolic']} mmHg / 舒張壓 {user['metrics']['blood_pressure_diastolic']} mmHg (2025 AHA 第一期高血壓)")
    print(f"  • 空腹血糖：{user['metrics']['fasting_glucose_mg_dl']} mg/dL | LDL-C: {user['metrics']['ldl_c_mg_dl']} mg/dL")
    print(f"  • TFDA 過敏原宣告：{user.get('allergens', [])}")

    # 3. Conversational Agent Turn 1
    user_msg_1 = "中午在公館附近，幫我推薦適合我高血壓與今日通勤步數的午餐！"
    print(f"\n[步驟 2] 使用者發送自然語言對話 (Turn 1)：")
    print(f"  💬 使用者：「{user_msg_1}」")

    chat_res_1 = agent.chat(
        user_message=user_msg_1,
        user_profile=user,
        user_lat=25.0135,
        user_lon=121.5342,
        activity_preset="moderate",
        meal_type="lunch"
    )

    print(f"\n[步驟 3] Agent 8 階段推理軌跡 (Reasoning Trace)：")
    for step in chat_res_1["reasoning_trace"]:
        print(f"  {step}")

    print("\n" + "=" * 75)
    print("🤖 NutriAgent 對談回覆與 Top-3 推薦結果：")
    print("=" * 75)
    print(chat_res_1["reply"])

    # 4. Conversational Agent Turn 2 (Feedback via Natural Language)
    user_msg_2 = "我覺得上一餐有點太油太重鹹了，請幫我調高清淡健康偏好並重新推薦！"
    print("\n" + "-" * 75)
    print(f"[步驟 4] 使用者發送自然語言回饋 (Turn 2 - Online Preference Update)：")
    print(f"  💬 使用者：「{user_msg_2}」")

    chat_res_2 = agent.chat(
        user_message=user_msg_2,
        user_profile=user,
        user_lat=25.0135,
        user_lon=121.5342,
        activity_preset="moderate",
        meal_type="lunch"
    )
    weights = chat_res_2["drl_flavor_weights"]
    print(f"  • 更新後之個人化口味偏好權重：")
    print(f"      - 清淡健康 (Light/Clean): {weights['light_clean']}")
    print(f"      - 傳統便當 (Bento/Savory): {weights['bento_savory']}")
    print(f"      - 高蛋白 (High-Protein): {weights['high_protein']}")
    print("=" * 75)
    print("✅ NutriAgent 對談式決策管線單次執行驗證完畢！\n")


if __name__ == "__main__":
    main()
