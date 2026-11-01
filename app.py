"""
NutriAgent - Interactive Web Cockpit & Demonstration Server
Module: app.py
Description: Full-stack interactive demonstration web interface powered by Flask.
Showcases real-time Google Fit IoT ingestion, clinical report constraint masking,
spatial map rendering, Top-3 dietary recommendations, and live PyTorch DRL weight updates.
"""

import json
from flask import Flask, render_template_string, request, jsonify
from src.agent import NutriAgent

app = Flask(__name__)
agent = NutriAgent()

# Load clinical test profiles
with open("data/sample_health_reports.json", "r", encoding="utf-8") as f:
    PROFILES_DATA = json.load(f)
    PROFILES = {p["profile_id"]: p for p in PROFILES_DATA}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NutriAgent 智動食健 - 即時適應性外食營養決策代理人</title>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700;900&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #10b981;
            --primary-dark: #059669;
            --secondary: #3b82f6;
            --accent: #f59e0b;
            --danger: #ef4444;
            --dark: #0f172a;
            --card-bg: rgba(30, 41, 59, 0.7);
            --card-border: rgba(255, 255, 255, 0.1);
            --text-main: #f8fafc;
            --text-sub: #94a3b8;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Noto Sans TC', sans-serif;
        }

        body {
            background: linear-gradient(135deg, #090d16 0%, #111827 50%, #0a1120 100%);
            color: var(--text-main);
            min-height: 100vh;
            padding: 24px 16px;
        }

        .container {
            max-width: 1280px;
            margin: 0 auto;
        }

        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: 20px;
            border-bottom: 1px solid var(--card-border);
            margin-bottom: 28px;
        }

        .brand-title {
            font-size: 26px;
            font-weight: 900;
            background: linear-gradient(90deg, #34d399, #38bdf8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .badge-agent {
            background: rgba(16, 185, 129, 0.15);
            border: 1px solid var(--primary);
            color: #6ee7b7;
            font-size: 13px;
            font-weight: 600;
            padding: 4px 10px;
            border-radius: 9999px;
            font-family: 'JetBrains Mono', monospace;
        }

        .grid-layout {
            display: grid;
            grid-template-columns: 380px 1fr;
            gap: 24px;
        }

        @media (max-width: 900px) {
            .grid-layout {
                grid-template-columns: 1fr;
            }
        }

        .glass-panel {
            background: var(--card-bg);
            backdrop-filter: blur(12px);
            border: 1px solid var(--card-border);
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
        }

        .section-header {
            font-size: 16px;
            font-weight: 700;
            color: #e2e8f0;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .form-group {
            margin-bottom: 16px;
        }

        label {
            display: block;
            font-size: 13px;
            font-weight: 600;
            color: var(--text-sub);
            margin-bottom: 6px;
        }

        select, input {
            width: 100%;
            padding: 10px 14px;
            background: rgba(15, 23, 42, 0.8);
            border: 1px solid var(--card-border);
            border-radius: 8px;
            color: #fff;
            font-size: 14px;
            outline: none;
            transition: border-color 0.2s;
        }

        select:focus, input:focus {
            border-color: var(--primary);
        }

        .health-radar-box {
            background: rgba(15, 23, 42, 0.6);
            border-radius: 10px;
            padding: 14px;
            margin-top: 10px;
            border-left: 3px solid var(--accent);
        }

        .metric-row {
            display: flex;
            justify-content: space-between;
            font-size: 13px;
            padding: 4px 0;
            border-bottom: 1px dashed rgba(255, 255, 255, 0.06);
        }

        .metric-row:last-child {
            border-bottom: none;
        }

        .metric-val {
            font-family: 'JetBrains Mono', monospace;
            font-weight: 600;
        }

        .val-danger { color: #f87171; }
        .val-warning { color: #fbbf24; }
        .val-safe { color: #34d399; }

        .btn-action {
            width: 100%;
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
            color: #ffffff;
            font-weight: 700;
            font-size: 15px;
            padding: 14px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            box-shadow: 0 4px 14px rgba(16, 185, 129, 0.4);
            transition: all 0.2s;
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 8px;
        }

        .btn-action:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(16, 185, 129, 0.5);
        }

        .status-strip {
            display: flex;
            gap: 12px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }

        .stat-card {
            flex: 1;
            min-width: 130px;
            background: rgba(30, 41, 59, 0.5);
            border: 1px solid var(--card-border);
            border-radius: 10px;
            padding: 12px;
            text-align: center;
        }

        .stat-card .num {
            font-size: 20px;
            font-weight: 900;
            font-family: 'JetBrains Mono', monospace;
            color: #38bdf8;
        }

        .stat-card .desc {
            font-size: 12px;
            color: var(--text-sub);
            margin-top: 4px;
        }

        .meal-card {
            background: rgba(30, 41, 59, 0.8);
            border: 1px solid var(--card-border);
            border-radius: 14px;
            padding: 20px;
            margin-bottom: 20px;
            transition: all 0.25s;
            position: relative;
            overflow: hidden;
        }

        .meal-card:hover {
            border-color: rgba(56, 189, 248, 0.4);
            transform: translateY(-2px);
            box-shadow: 0 12px 28px rgba(0, 0, 0, 0.4);
        }

        .card-top {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 12px;
        }

        .rank-badge {
            background: #0284c7;
            color: #fff;
            font-size: 12px;
            font-weight: 700;
            padding: 4px 10px;
            border-radius: 6px;
            font-family: 'JetBrains Mono', monospace;
        }

        .rank-1 { background: linear-gradient(135deg, #10b981, #059669); }
        .rank-2 { background: linear-gradient(135deg, #0284c7, #0369a1); }
        .rank-3 { background: linear-gradient(135deg, #6366f1, #4f46e5); }

        .dish-title {
            font-size: 18px;
            font-weight: 700;
            color: #f1f5f9;
        }

        .store-info {
            font-size: 13px;
            color: var(--text-sub);
            margin-top: 2px;
        }

        .nutri-bars {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 8px;
            background: rgba(15, 23, 42, 0.6);
            padding: 12px;
            border-radius: 8px;
            margin: 12px 0;
            text-align: center;
        }

        .nutri-item .lbl {
            font-size: 11px;
            color: var(--text-sub);
        }

        .nutri-item .val {
            font-size: 15px;
            font-weight: 700;
            font-family: 'JetBrains Mono', monospace;
            margin-top: 2px;
            color: #e2e8f0;
        }

        .explanation-box {
            background: rgba(16, 185, 129, 0.08);
            border: 1px solid rgba(16, 185, 129, 0.25);
            border-radius: 8px;
            padding: 12px 14px;
            font-size: 13px;
            color: #a7f3d0;
            line-height: 1.6;
            margin-bottom: 14px;
        }

        .card-actions {
            display: flex;
            gap: 10px;
        }

        .btn-feedback {
            flex: 1;
            padding: 9px 12px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            border: 1px solid transparent;
            transition: all 0.15s;
        }

        .btn-accept {
            background: rgba(16, 185, 129, 0.2);
            border-color: var(--primary);
            color: #34d399;
        }

        .btn-accept:hover {
            background: var(--primary);
            color: #fff;
        }

        .btn-reject {
            background: rgba(239, 68, 68, 0.15);
            border-color: rgba(239, 68, 68, 0.4);
            color: #f87171;
        }

        .btn-reject:hover {
            background: var(--danger);
            color: #fff;
        }

        .btn-skip {
            background: rgba(148, 163, 184, 0.15);
            border-color: rgba(148, 163, 184, 0.3);
            color: var(--text-sub);
        }

        .btn-skip:hover {
            background: #475569;
            color: #fff;
        }

        .tag-pill {
            display: inline-block;
            font-size: 11px;
            background: rgba(255, 255, 255, 0.08);
            padding: 2px 8px;
            border-radius: 4px;
            color: #cbd5e1;
            margin-right: 4px;
        }

        .flavor-monitor {
            display: flex;
            gap: 8px;
            margin-top: 10px;
        }

        .flavor-bar-item {
            flex: 1;
            background: rgba(15, 23, 42, 0.5);
            border-radius: 6px;
            padding: 8px;
            text-align: center;
        }

        .flavor-bar-item .val {
            font-family: 'JetBrains Mono', monospace;
            font-weight: 700;
            color: #38bdf8;
            font-size: 13px;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="brand-title">
                <span>🥗 NutriAgent</span>
                <span class="badge-agent">Domain AI Agent v1.0</span>
            </div>
            <div style="font-size: 13px; color: var(--text-sub);">
                物聯網應用與資料分析 Final Project
            </div>
        </header>

        <div class="grid-layout">
            <!-- Left Column: Context & Input Controls -->
            <div>
                <div class="glass-panel">
                    <div class="section-header">👤 使用者與健檢報告 (Clinical Profile)</div>
                    <div class="form-group">
                        <label>選擇使用者檔案</label>
                        <select id="userSelect" onchange="updateProfileView()">
                            {% for pid, p in profiles.items() %}
                            <option value="{{ pid }}">{{ p.name }}</option>
                            {% endfor %}
                        </select>
                    </div>

                    <div id="profileDetails" class="health-radar-box">
                        <!-- Populated by JS -->
                    </div>
                </div>

                <div class="glass-panel">
                    <div class="section-header">⌚ Google Fit 物聯網即時串流 (IoT Telemetry)</div>
                    <div class="form-group">
                        <label>當前生理活動狀態模擬</label>
                        <select id="activityPreset">
                            <option value="moderate" selected>一般通勤步行 (步數 ~6,800 / 消耗 320 kcal)</option>
                            <option value="sedentary">久坐讀書/辦公 (步數 ~1,850 / 消耗 110 kcal)</option>
                            <option value="high_active">高強度重訓/跑步 (步數 ~14,200 / 消耗 680 kcal)</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>用餐時段</label>
                        <select id="mealType">
                            <option value="lunch" selected>午餐 (Lunch / 40% 配額)</option>
                            <option value="dinner">晚餐 (Dinner / 35% 配額)</option>
                            <option value="breakfast">早餐 (Breakfast / 25% 配額)</option>
                        </select>
                    </div>
                </div>

                <div class="glass-panel">
                    <div class="section-header">📍 活動區域與 LBS (Geospatial)</div>
                    <div class="form-group">
                        <label>當前位置 (商圈/校園)</label>
                        <select id="locationSelect">
                            <option value="25.0135,121.5342">台大公館商圈 (Gongguan Center)</option>
                            <option value="25.0268,121.5358">大安森林公園周邊 (Daan)</option>
                            <option value="25.0350,121.5645">信義微風商圈 (Xinyi District)</option>
                        </select>
                    </div>

                    <button class="btn-action" onclick="fetchRecommendations()">
                        <span>⚡ 執行即時適應性推薦 (Run Agent)</span>
                    </button>
                </div>

                <div class="glass-panel">
                    <div class="section-header">🧠 深度強化學習口味偏好 (DRL Weights)</div>
                    <div style="font-size: 12px; color: var(--text-sub); margin-bottom: 8px;">
                        點擊餐點反饋後即時觸發 PyTorch 策略網路梯度更新
                    </div>
                    <div class="flavor-monitor">
                        <div class="flavor-bar-item">
                            <div style="font-size: 11px; color: var(--text-sub);">清淡健康</div>
                            <div class="val" id="weightClean">0.500</div>
                        </div>
                        <div class="flavor-bar-item">
                            <div style="font-size: 11px; color: var(--text-sub);">傳統便當</div>
                            <div class="val" id="weightSavory">0.500</div>
                        </div>
                        <div class="flavor-bar-item">
                            <div style="font-size: 11px; color: var(--text-sub);">高蛋白</div>
                            <div class="val" id="weightProtein">0.500</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Right Column: Results & Interactive Cards -->
            <div>
                <!-- Status Metrics Strip -->
                <div class="status-strip" id="statusStrip" style="display: none;">
                    <div class="stat-card">
                        <div class="num" id="statTDEE">--</div>
                        <div class="desc">動態 TDEE (kcal)</div>
                    </div>
                    <div class="stat-card">
                        <div class="num" id="statBudget">--</div>
                        <div class="desc">當餐熱量預算 (kcal)</div>
                    </div>
                    <div class="stat-card">
                        <div class="num" id="statSafe">--</div>
                        <div class="desc">安全餐點 (通過臨床篩檢)</div>
                    </div>
                    <div class="stat-card">
                        <div class="num" style="color: #f87171;" id="statRejected">--</div>
                        <div class="desc">醫學硬約束剔除 (禁忌)</div>
                    </div>
                </div>

                <!-- Recommendations Container -->
                <div id="resultsContainer">
                    <div class="glass-panel" style="text-align: center; padding: 60px 20px; color: var(--text-sub);">
                        <div style="font-size: 40px; margin-bottom: 12px;">🥗</div>
                        <h3 style="color: #f8fafc; margin-bottom: 8px;">準備就緒</h3>
                        <p style="font-size: 14px;">請於左側設定您的健康狀況與活動量，點擊「執行即時適應性推薦」啟動 NutriAgent 決策引擎。</p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const profiles = {{ profiles | tojson }};

        function updateProfileView() {
            const selId = document.getElementById("userSelect").value;
            const p = profiles[selId];
            const m = p.metrics;

            let html = `
                <div style="font-weight: 700; color: #f8fafc; margin-bottom: 6px;">${p.name}</div>
                <div style="font-size: 12px; color: var(--text-sub); margin-bottom: 10px;">${p.description}</div>
                <div class="metric-row">
                    <span>血壓 (BP)</span>
                    <span class="metric-val ${m.blood_pressure_systolic >= 130 ? 'val-danger' : 'val-safe'}">${m.blood_pressure_systolic}/${m.blood_pressure_diastolic} mmHg</span>
                </div>
                <div class="metric-row">
                    <span>空腹血糖 (FG)</span>
                    <span class="metric-val ${m.fasting_glucose_mg_dl >= 100 ? 'val-danger' : 'val-safe'}">${m.fasting_glucose_mg_dl} mg/dL</span>
                </div>
                <div class="metric-row">
                    <span>血尿酸 (UA)</span>
                    <span class="metric-val ${m.uric_acid_mg_dl >= 7.0 ? 'val-danger' : 'val-safe'}">${m.uric_acid_mg_dl} mg/dL</span>
                </div>
                <div class="metric-row">
                    <span>低密度脂蛋白 (LDL)</span>
                    <span class="metric-val ${m.ldl_c_mg_dl >= 130 ? 'val-warning' : 'val-safe'}">${m.ldl_c_mg_dl} mg/dL</span>
                </div>
                <div class="metric-row">
                    <span>身體質量指數 (BMI)</span>
                    <span class="metric-val">${m.bmi}</span>
                </div>
            `;
            document.getElementById("profileDetails").innerHTML = html;
        }

        async function fetchRecommendations() {
            const selId = document.getElementById("userSelect").value;
            const activity = document.getElementById("activityPreset").value;
            const mealType = document.getElementById("mealType").value;
            const locCoords = document.getElementById("locationSelect").value.split(",");
            const lat = parseFloat(locCoords[0]);
            const lon = parseFloat(locCoords[1]);

            document.getElementById("resultsContainer").innerHTML = `
                <div class="glass-panel" style="text-align: center; padding: 50px;">
                    <div style="font-size: 24px;">⚙️ NutriAgent 正在運算最佳外食配額與臨床安全篩選...</div>
                </div>
            `;

            try {
                const res = await fetch("/api/recommend", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({
                        profile_id: selId,
                        activity_preset: activity,
                        meal_type: mealType,
                        lat: lat,
                        lon: lon
                    })
                });
                const data = await res.json();
                renderResults(data);
            } catch (err) {
                alert("推薦呼叫失敗: " + err);
            }
        }

        function renderResults(data) {
            // Update Strip
            document.getElementById("statusStrip").style.display = "flex";
            document.getElementById("statTDEE").innerText = data.metabolic_budget.dynamic_tdee_kcal;
            document.getElementById("statBudget").innerText = data.metabolic_budget.target_meal_calories;
            document.getElementById("statSafe").innerText = data.spatial_context.safe_candidates_count;
            document.getElementById("statRejected").innerText = data.spatial_context.clinical_rejected_count;

            // Update Flavor Weights
            if (data.drl_flavor_weights) {
                document.getElementById("weightClean").innerText = data.drl_flavor_weights.light_clean;
                document.getElementById("weightSavory").innerText = data.drl_flavor_weights.bento_savory;
                document.getElementById("weightProtein").innerText = data.drl_flavor_weights.high_protein;
            }

            // Render Cards
            let cardsHtml = "";
            data.recommendations.forEach((m, idx) => {
                const rankClass = idx === 0 ? "rank-1" : (idx === 1 ? "rank-2" : "rank-3");
                const tags = (m.tags || []).map(t => `<span class="tag-pill">${t}</span>`).join("");

                cardsHtml += `
                    <div class="meal-card" id="card-${m.meal_id}">
                        <div class="card-top">
                            <div>
                                <span class="rank-badge ${rankClass}">Top ${m.rank} 推薦</span>
                                <div class="dish-title" style="margin-top: 6px;">${m.dish_name}</div>
                                <div class="store-info">🏪 ${m.store_name} · 🚶 距離 ${m.distance_km} km (步行約 ${m.walking_time_min} 分鐘) · NT$ ${m.price_twd}</div>
                            </div>
                        </div>

                        <div style="margin: 6px 0;">${tags}</div>

                        <div class="nutri-bars">
                            <div class="nutri-item">
                                <div class="lbl">總熱量</div>
                                <div class="val" style="color: #38bdf8;">${m.calories_kcal} <span style="font-size:11px;">kcal</span></div>
                            </div>
                            <div class="nutri-item">
                                <div class="lbl">蛋白質</div>
                                <div class="val">${m.protein_g} <span style="font-size:11px;">g</span></div>
                            </div>
                            <div class="nutri-item">
                                <div class="lbl">脂肪</div>
                                <div class="val">${m.fat_g} <span style="font-size:11px;">g</span></div>
                            </div>
                            <div class="nutri-item">
                                <div class="lbl">鈉含量</div>
                                <div class="val ${m.sodium_mg > 700 ? 'val-danger' : 'val-safe'}">${m.sodium_mg} <span style="font-size:11px;">mg</span></div>
                            </div>
                        </div>

                        <div class="explanation-box">
                            💡 <strong>臨床與代謝決策理由：</strong><br/>
                            ${m.clinical_explanation}
                        </div>

                        <div class="card-actions">
                            <button class="btn-feedback btn-accept" onclick="sendFeedback('${m.meal_id}', 'accept')">
                                ✔️ 採納並前往
                            </button>
                            <button class="btn-feedback btn-reject" onclick="sendFeedback('${m.meal_id}', 'too_oily')">
                                🍳 太油 / 太鹹
                            </button>
                            <button class="btn-feedback btn-skip" onclick="sendFeedback('${m.meal_id}', 'skip')">
                                ⏭️ 換別家
                            </button>
                        </div>
                    </div>
                `;
            });

            document.getElementById("resultsContainer").innerHTML = cardsHtml;
        }

        async function sendFeedback(mealId, feedbackType) {
            try {
                const res = await fetch("/api/feedback", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({
                        meal_id: mealId,
                        feedback_type: feedbackType
                    })
                });
                const data = await res.json();
                if (data.status === "success") {
                    // Update weights display
                    document.getElementById("weightClean").innerText = data.updated_flavor_weights.light_clean;
                    document.getElementById("weightSavory").innerText = data.updated_flavor_weights.bento_savory;
                    document.getElementById("weightProtein").innerText = data.updated_flavor_weights.high_protein;

                    const labelMap = {
                        "accept": "已記錄採納！強化學習策略已將正向回報寫入 Replay Buffer 🏆",
                        "too_oily": "已收到反饋：太油太重鹹！策略網路已即時降低油膩餐點權重 ⚡",
                        "skip": "已略過！模型已記錄探索偏好 ⏭️"
                    };
                    alert(labelMap[feedbackType] + ` (損失值: ${data.online_training_loss})`);
                }
            } catch (err) {
                alert("反饋送出失敗: " + err);
            }
        }

        // Initialize view on load
        window.onload = updateProfileView;
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE, profiles=PROFILES)

@app.route("/api/recommend", methods=["POST"])
def api_recommend():
    data = request.get_json() or {}
    profile_id = data.get("profile_id", "P_001_HYPERTENSION")
    user_profile = PROFILES.get(profile_id, PROFILES["P_001_HYPERTENSION"])

    lat = float(data.get("lat", 25.0135))
    lon = float(data.get("lon", 121.5342))
    activity_preset = data.get("activity_preset", "moderate")
    meal_type = data.get("meal_type", "lunch")

    result = agent.run_recommendation(
        user_profile=user_profile,
        user_lat=lat,
        user_lon=lon,
        activity_preset=activity_preset,
        meal_type=meal_type
    )
    return jsonify(result)

@app.route("/api/feedback", methods=["POST"])
def api_feedback():
    data = request.get_json() or {}
    meal_id = data.get("meal_id", "")
    feedback_type = data.get("feedback_type", "accept")

    res = agent.handle_user_feedback(meal_id=meal_id, feedback_type=feedback_type)
    return jsonify(res)

if __name__ == "__main__":
    print("==================================================================")
    print("🥗 NutriAgent Cockpit Server starting at http://127.0.0.1:5000 ...")
    print("==================================================================")
    app.run(host="127.0.0.1", port=5000, debug=False)
