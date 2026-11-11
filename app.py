"""
NutriAgent - ChatGPT-Style Conversational AI Agent Web Interface
Module: app.py
Description: Interactive conversational web application powered by Flask & Google Gemini API.
Combines multi-turn natural language dialogue with real-time wearable IoT telemetry,
deterministic clinical & TFDA-11 allergen hard-constraint gating, spatial LBS retrieval,
and online preference adaptation.
"""

import os
import json
from pathlib import Path
from flask import Flask, render_template_string, request, jsonify
from src.agent import NutriAgent

app = Flask(__name__)
agent = NutriAgent(api_key=os.environ.get("GEMINI_API_KEY", ""))

BASE_DIR = Path(__file__).resolve().parent
PROFILES_PATH = BASE_DIR / "data" / "sample_health_reports.json"

with open(PROFILES_PATH, "r", encoding="utf-8") as f:
    PROFILES_DATA = json.load(f)
    PROFILES = {p["profile_id"]: p for p in PROFILES_DATA}

HTML_TEMPLATE = r"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NutriAgent 智動食健 — Gemini 臨床營養與穿戴 IoT 對談式決策代理人</title>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700;900&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-main: #0b0f19;
            --bg-sidebar: #111827;
            --bg-card: rgba(30, 41, 59, 0.75);
            --bg-user-msg: #059669;
            --bg-agent-msg: rgba(30, 41, 59, 0.85);
            --border-color: rgba(255, 255, 255, 0.1);
            --primary: #10b981;
            --primary-hover: #059669;
            --accent: #38bdf8;
            --warning: #f59e0b;
            --danger: #ef4444;
            --text-main: #f8fafc;
            --text-sub: #94a3b8;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Noto Sans TC', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        body {
            background-color: var(--bg-main);
            color: var(--text-main);
            height: 100vh;
            display: flex;
            overflow: hidden;
        }

        /* Left Sidebar (ChatGPT Style) */
        .sidebar {
            width: 360px;
            min-width: 360px;
            background-color: var(--bg-sidebar);
            border-right: 1px solid var(--border-color);
            display: flex;
            flex-direction: column;
            height: 100vh;
            overflow-y: auto;
            padding: 16px;
            gap: 14px;
        }

        .sidebar::-webkit-scrollbar, .chat-stream::-webkit-scrollbar {
            width: 6px;
        }
        .sidebar::-webkit-scrollbar-thumb, .chat-stream::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.15);
            border-radius: 3px;
        }

        .brand-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: 12px;
            border-bottom: 1px solid var(--border-color);
        }

        .brand-logo {
            font-size: 20px;
            font-weight: 900;
            background: linear-gradient(90deg, #34d399, #38bdf8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .btn-new-chat {
            background: rgba(16, 185, 129, 0.15);
            border: 1px solid var(--primary);
            color: #6ee7b7;
            font-size: 12px;
            font-weight: 600;
            padding: 6px 12px;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s;
        }

        .btn-new-chat:hover {
            background: var(--primary);
            color: #fff;
        }

        .side-card {
            background: rgba(15, 23, 42, 0.7);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 12px;
        }

        .side-title {
            font-size: 13px;
            font-weight: 700;
            color: #e2e8f0;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .form-row {
            margin-bottom: 8px;
        }
        .form-row:last-child {
            margin-bottom: 0;
        }

        label {
            display: block;
            font-size: 11px;
            font-weight: 600;
            color: var(--text-sub);
            margin-bottom: 4px;
        }

        select, input[type="password"], input[type="text"] {
            width: 100%;
            padding: 8px 10px;
            background: rgba(9, 13, 22, 0.9);
            border: 1px solid var(--border-color);
            border-radius: 7px;
            color: #fff;
            font-size: 12.5px;
            outline: none;
        }

        select:focus, input:focus {
            border-color: var(--primary);
        }

        .api-key-group {
            display: flex;
            gap: 6px;
        }

        .btn-save-key {
            background: var(--accent);
            color: #0f172a;
            border: none;
            border-radius: 7px;
            padding: 0 12px;
            font-size: 12px;
            font-weight: 700;
            cursor: pointer;
            white-space: nowrap;
        }

        .status-pill {
            font-size: 11px;
            padding: 2px 8px;
            border-radius: 999px;
            font-family: 'JetBrains Mono', monospace;
        }
        .status-online {
            background: rgba(16, 185, 129, 0.2);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.4);
        }
        .status-local {
            background: rgba(56, 189, 248, 0.15);
            color: #7dd3fc;
            border: 1px solid rgba(56, 189, 248, 0.35);
        }

        .metrics-mini {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 6px;
            margin-top: 8px;
        }

        .metric-chip {
            background: rgba(30, 41, 59, 0.6);
            padding: 5px 8px;
            border-radius: 6px;
            font-size: 11px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .val-danger { color: #f87171; font-weight: 700; font-family: 'JetBrains Mono', monospace; }
        .val-warning { color: #fbbf24; font-weight: 700; font-family: 'JetBrains Mono', monospace; }
        .val-safe { color: #34d399; font-weight: 600; font-family: 'JetBrains Mono', monospace; }

        .allergen-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 5px;
            max-height: 155px;
            overflow-y: auto;
            padding-right: 2px;
        }

        .allergen-item {
            display: flex;
            align-items: center;
            gap: 5px;
            font-size: 11.5px;
            color: #cbd5e1;
            background: rgba(30, 41, 59, 0.5);
            padding: 5px 7px;
            border-radius: 5px;
            cursor: pointer;
            margin: 0;
        }

        .allergen-item input {
            accent-color: var(--danger);
        }

        .weights-strip {
            display: flex;
            gap: 6px;
            margin-top: 6px;
        }

        .weight-box {
            flex: 1;
            background: rgba(30, 41, 59, 0.6);
            border-radius: 6px;
            padding: 6px;
            text-align: center;
        }

        .weight-box .lbl { font-size: 10px; color: var(--text-sub); }
        .weight-box .val { font-size: 13px; font-weight: 700; color: var(--accent); font-family: 'JetBrains Mono', monospace; }

        /* Main Chat Area */
        .main-pane {
            flex: 1;
            display: flex;
            flex-direction: column;
            height: 100vh;
            background: radial-gradient(circle at top right, #131c31 0%, #0b0f19 65%);
        }

        /* Top Telemetry Bar */
        .top-bar {
            height: 58px;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 24px;
            background: rgba(17, 24, 39, 0.8);
            backdrop-filter: blur(10px);
        }

        .top-stats {
            display: flex;
            gap: 20px;
            align-items: center;
        }

        .top-stat-item {
            font-size: 12.5px;
            color: var(--text-sub);
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .top-stat-item strong {
            color: #f8fafc;
            font-family: 'JetBrains Mono', monospace;
            font-size: 14px;
        }

        /* Chat Stream */
        .chat-stream {
            flex: 1;
            overflow-y: auto;
            padding: 24px 10%;
            display: flex;
            flex-direction: column;
            gap: 20px;
        }

        @media (max-width: 1100px) {
            .chat-stream { padding: 20px 24px; }
            .sidebar { width: 300px; min-width: 300px; }
        }

        .msg-row {
            display: flex;
            gap: 14px;
            align-items: flex-start;
            animation: fadeIn 0.25s ease;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(6px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .msg-row.user {
            flex-direction: row-reverse;
        }

        .avatar {
            width: 36px;
            height: 36px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            flex-shrink: 0;
        }

        .avatar.agent {
            background: linear-gradient(135deg, #10b981, #0284c7);
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
        }

        .avatar.user {
            background: #334155;
        }

        .msg-bubble {
            max-width: 82%;
            padding: 16px 20px;
            border-radius: 16px;
            font-size: 14.5px;
            line-height: 1.65;
        }

        .msg-row.user .msg-bubble {
            background: linear-gradient(135deg, #059669, #047857);
            color: #fff;
            border-top-right-radius: 4px;
        }

        .msg-row.agent .msg-bubble {
            background: var(--bg-agent-msg);
            border: 1px solid var(--border-color);
            color: var(--text-main);
            border-top-left-radius: 4px;
            width: 100%;
        }

        /* Reasoning Trace Accordion */
        details.trace-box {
            background: rgba(15, 23, 42, 0.75);
            border: 1px solid rgba(56, 189, 248, 0.25);
            border-radius: 10px;
            padding: 8px 12px;
            margin-bottom: 14px;
            font-size: 12px;
            color: #93c5fd;
        }

        details.trace-box summary {
            cursor: pointer;
            font-weight: 700;
            user-select: none;
            outline: none;
        }

        .trace-step {
            margin-top: 6px;
            padding-left: 10px;
            border-left: 2px solid #38bdf8;
            color: #cbd5e1;
            line-height: 1.5;
        }

        /* Prompt Suggestion Chips */
        .chips-wrap {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 14px;
        }

        .prompt-chip {
            background: rgba(30, 41, 59, 0.9);
            border: 1px solid rgba(56, 189, 248, 0.3);
            color: #e2e8f0;
            padding: 8px 14px;
            border-radius: 999px;
            font-size: 12.5px;
            cursor: pointer;
            transition: all 0.2s;
        }

        .prompt-chip:hover {
            background: rgba(16, 185, 129, 0.2);
            border-color: var(--primary);
            color: #fff;
            transform: translateY(-1px);
        }

        /* Embedded Meal Cards inside Chat Bubble */
        .chat-cards-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 12px;
            margin-top: 16px;
        }

        .chat-meal-card {
            background: rgba(15, 23, 42, 0.85);
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 12px;
            padding: 14px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: border-color 0.2s;
        }

        .chat-meal-card:hover {
            border-color: var(--accent);
        }

        .card-badge-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 6px;
        }

        .rank-tag {
            font-size: 11px;
            font-weight: 700;
            padding: 2px 8px;
            border-radius: 5px;
            font-family: 'JetBrains Mono', monospace;
            background: #0284c7;
            color: #fff;
        }
        .rank-1 { background: linear-gradient(135deg, #10b981, #059669); }
        .rank-2 { background: linear-gradient(135deg, #0284c7, #0369a1); }
        .rank-3 { background: linear-gradient(135deg, #6366f1, #4f46e5); }

        .nutri-mini-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 4px;
            background: rgba(30, 41, 59, 0.6);
            padding: 8px;
            border-radius: 8px;
            margin: 10px 0;
            text-align: center;
        }

        .nutri-mini-grid .n-lbl { font-size: 10px; color: var(--text-sub); }
        .nutri-mini-grid .n-val { font-size: 12.5px; font-weight: 700; font-family: 'JetBrains Mono', monospace; color: #f8fafc; }

        .card-btn-row {
            display: flex;
            gap: 6px;
            margin-top: 10px;
        }

        .card-btn {
            flex: 1;
            padding: 6px 8px;
            font-size: 11.5px;
            font-weight: 600;
            border-radius: 6px;
            cursor: pointer;
            border: 1px solid transparent;
            transition: all 0.15s;
        }
        .c-accept { background: rgba(16, 185, 129, 0.2); border-color: var(--primary); color: #6ee7b7; }
        .c-accept:hover { background: var(--primary); color: #fff; }
        .c-oily { background: rgba(239, 68, 68, 0.15); border-color: rgba(239, 68, 68, 0.4); color: #fca5a5; }
        .c-oily:hover { background: var(--danger); color: #fff; }
        .c-skip { background: rgba(148, 163, 184, 0.15); border-color: rgba(148, 163, 184, 0.3); color: #cbd5e1; }
        .c-skip:hover { background: #475569; color: #fff; }

        /* Chat Input Dock */
        .input-dock {
            padding: 16px 10% 20px;
            background: linear-gradient(180deg, transparent 0%, rgba(11, 15, 25, 0.95) 30%);
        }

        @media (max-width: 1100px) {
            .input-dock { padding: 12px 24px 16px; }
        }

        .input-box-wrapper {
            background: rgba(30, 41, 59, 0.9);
            border: 1px solid rgba(255, 255, 255, 0.18);
            border-radius: 14px;
            padding: 10px 14px;
            display: flex;
            align-items: center;
            gap: 10px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
        }

        .input-box-wrapper:focus-within {
            border-color: var(--primary);
        }

        textarea#chatInput {
            flex: 1;
            background: transparent;
            border: none;
            color: #fff;
            font-size: 14.5px;
            resize: none;
            outline: none;
            max-height: 110px;
            line-height: 1.5;
        }

        .btn-send {
            background: linear-gradient(135deg, var(--primary), var(--primary-hover));
            color: #fff;
            border: none;
            width: 40px;
            height: 40px;
            border-radius: 10px;
            font-size: 16px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            transition: transform 0.15s;
        }

        .btn-send:hover {
            transform: scale(1.05);
        }

        .disclaimer-foot {
            text-align: center;
            font-size: 11px;
            color: var(--text-sub);
            margin-top: 8px;
        }

        .md-content h3 {
            font-size: 15px;
            color: #6ee7b7;
            margin: 12px 0 6px;
        }
        .md-content ul {
            padding-left: 20px;
            margin: 6px 0;
        }
        .md-content li {
            margin-bottom: 4px;
        }
        .md-content code {
            background: rgba(15, 23, 42, 0.8);
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 12.5px;
            color: #38bdf8;
        }
    </style>
</head>
<body>
    <!-- Left Sidebar: Profile, TFDA-11 Allergens, Wearable IoT, Gemini API Settings -->
    <aside class="sidebar">
        <div class="brand-row">
            <div class="brand-logo">
                <span>🥗 NutriAgent</span>
            </div>
            <button class="btn-new-chat" onclick="resetConversation()">＋ 新對話</button>
        </div>

        <!-- Gemini API Key Setup -->
        <div class="side-card">
            <div class="side-title">
                <span>✨ Gemini API 引擎設定</span>
                <span id="geminiStatusBadge" class="status-pill {{ 'status-online' if gemini_configured else 'status-local' }}">
                    {{ '🟢 Gemini 已連線' if gemini_configured else '⚡ 內建接地引擎' }}
                </span>
            </div>
            <div class="form-row">
                <label>Google Gemini API Key (選填，未填自動使用內建臨床語義引擎)</label>
                <div class="api-key-group">
                    <input type="password" id="geminiApiKey" placeholder="輸入 AIzaSy... 金鑰串接 Gemini">
                    <button class="btn-save-key" onclick="saveApiKey()">套用</button>
                </div>
            </div>
            <div class="form-row">
                <label>Gemini 模型選擇</label>
                <select id="geminiModel" onchange="saveApiKey()">
                    <option value="gemini-2.5-flash" selected>gemini-2.5-flash (推薦・極速)</option>
                    <option value="gemini-2.0-flash">gemini-2.0-flash</option>
                    <option value="gemini-1.5-pro">gemini-1.5-pro</option>
                </select>
            </div>
        </div>

        <!-- User Clinical Profile -->
        <div class="side-card">
            <div class="side-title">👤 健檢報告與臨床表型 (Profile)</div>
            <div class="form-row">
                <select id="userSelect" onchange="updateProfileView()">
                    {% for pid, p in profiles.items() %}
                    <option value="{{ pid }}">{{ p.name }}</option>
                    {% endfor %}
                </select>
            </div>
            <div id="profileDesc" style="font-size: 11px; color: var(--text-sub); line-height: 1.4;"></div>
            <div id="profileMetrics" class="metrics-mini"></div>
        </div>

        <!-- TFDA 11 Mandatory Allergens -->
        <div class="side-card">
            <div class="side-title">
                <span>🛡️ TFDA 11 類強制過敏原閘門</span>
                <span style="font-size: 10px; color: #f87171;">AVR = 0%</span>
            </div>
            <div class="allergen-grid">
                <label class="allergen-item"><input type="checkbox" value="seafood" id="allg_seafood"> 🦐 海鮮綜合</label>
                <label class="allergen-item"><input type="checkbox" value="crustacean" id="allg_crustacean"> 🦀 甲殼類</label>
                <label class="allergen-item"><input type="checkbox" value="fish" id="allg_fish"> 🐟 魚類</label>
                <label class="allergen-item"><input type="checkbox" value="peanuts" id="allg_peanuts"> 🥜 花生</label>
                <label class="allergen-item"><input type="checkbox" value="tree_nuts" id="allg_tree_nuts"> 🌰 堅果類</label>
                <label class="allergen-item"><input type="checkbox" value="gluten" id="allg_gluten"> 🌾 含麩質穀物</label>
                <label class="allergen-item"><input type="checkbox" value="dairy" id="allg_dairy"> 🥛 牛奶/羊奶</label>
                <label class="allergen-item"><input type="checkbox" value="egg" id="allg_egg"> 🥚 蛋類</label>
                <label class="allergen-item"><input type="checkbox" value="soy" id="allg_soy"> 🫘 大豆/黃豆</label>
                <label class="allergen-item"><input type="checkbox" value="sesame" id="allg_sesame"> 🌿 芝麻</label>
                <label class="allergen-item"><input type="checkbox" value="mango" id="allg_mango"> 🥭 芒果</label>
                <label class="allergen-item"><input type="checkbox" value="sulfites" id="allg_sulfites"> 🧪 亞硫酸鹽</label>
            </div>
        </div>

        <!-- Wearable IoT & LBS Context -->
        <div class="side-card">
            <div class="side-title">⌚ 穿戴式 IoT 活動與 📍 商圈定位</div>
            <div class="form-row">
                <label>Health Connect / 穿戴式活動量模擬</label>
                <select id="activityPreset">
                    <option value="moderate" selected>一般通勤步行 (~6,800 步 / 320 kcal)</option>
                    <option value="sedentary">久坐辦公/讀書 (~1,850 步 / 110 kcal)</option>
                    <option value="high_active">高強度訓練 (~14,200 步 / 680 kcal)</option>
                    <option value="vibration_artifact">⚠️ 車上震動假步數測試 (15,000步/心率66)</option>
                    <option value="offline_timeout">🔌 穿戴裝置逾時降級測試 (LOW_CONF)</option>
                </select>
            </div>
            <div class="form-row" style="display: grid; grid-template-columns: 1fr 1fr; gap: 6px;">
                <div>
                    <label>預設時段</label>
                    <select id="mealType">
                        <option value="lunch" selected>午餐 (40%)</option>
                        <option value="dinner">晚餐 (35%)</option>
                        <option value="breakfast">早餐 (25%)</option>
                    </select>
                </div>
                <div>
                    <label>預設商圈座標</label>
                    <select id="locationSelect">
                        <option value="25.0135,121.5342">台大公館商圈</option>
                        <option value="25.0268,121.5358">大安森林公園</option>
                        <option value="25.0350,121.5645">信義微風商圈</option>
                    </select>
                </div>
            </div>
        </div>

        <!-- Online Preference Weights -->
        <div class="side-card">
            <div class="side-title">🧠 個人化口味偏好記憶 (Online Weights)</div>
            <div class="weights-strip">
                <div class="weight-box">
                    <div class="lbl">清淡健康</div>
                    <div class="val" id="weightClean">0.500</div>
                </div>
                <div class="weight-box">
                    <div class="lbl">傳統便當</div>
                    <div class="val" id="weightSavory">0.500</div>
                </div>
                <div class="weight-box">
                    <div class="lbl">高蛋白</div>
                    <div class="val" id="weightProtein">0.500</div>
                </div>
            </div>
        </div>
    </aside>

    <!-- Main ChatGPT-style Conversational Pane -->
    <main class="main-pane">
        <!-- Top Status Bar -->
        <div class="top-bar">
            <div class="top-stats">
                <div class="top-stat-item">🔥 動態 TDEE: <strong id="statTDEE">-- kcal</strong></div>
                <div class="top-stat-item">🎯 當餐預算: <strong id="statBudget">-- kcal</strong></div>
                <div class="top-stat-item">✅ 安全候選池: <strong id="statSafe" style="color: #34d399;">-- 道</strong></div>
                <div class="top-stat-item">🚫 臨床/過敏剔除: <strong id="statRejected" style="color: #f87171;">-- 道</strong></div>
            </div>
            <div style="font-size: 12px; color: var(--text-sub);">
                CVR = 0.0% ｜ AVR = 0.0% (Deterministic Gate)
            </div>
        </div>

        <!-- Scrollable Conversation Stream -->
        <div class="chat-stream" id="chatStream">
            <!-- Initial Agent Welcome Message -->
            <div class="msg-row agent">
                <div class="avatar agent">🥗</div>
                <div class="msg-bubble">
                    <div style="font-weight: 700; color: #34d399; margin-bottom: 6px;">
                        NutriAgent 臨床外食決策代理人
                    </div>
                    <p>您好！我是結合 **穿戴式 IoT 動態代謝**、**臨床營養硬約束閘門 (2025 AHA/ACC 高血壓、ADA 2026 糖尿病、2020 ACR 痛風、TFDA 11 類過敏原)** 與 **Google Gemini API** 的對談式外食決策 Agent。</p>
                    <p style="margin-top: 8px; color: #cbd5e1; font-size: 13.5px;">
                        您可以直接在下方用自然語言告訴我您現在想吃什麼、在哪裡、或是詢問某道餐點能不能吃，也可以直接點擊下方快捷提問開始對話：
                    </p>
                    <div class="chips-wrap">
                        <button class="prompt-chip" onclick="sendQuickPrompt('中午在公館附近，幫我根據健檢報告與今日步數推薦適合的午餐！')">🍱 推薦公館附近適合我健檢狀況的午餐</button>
                        <button class="prompt-chip" onclick="sendQuickPrompt('我今天剛高強度運動完消耗很多熱量，想吃高蛋白且不油膩的餐點')">🏋️ 剛運動完想補充高蛋白餐點</button>
                        <button class="prompt-chip" onclick="sendQuickPrompt('為什麼我不能吃酥炸大排骨便當或老先覺麻辣鍋？可以幫我分析原因嗎？')">🚫 為什麼我不能吃炸排骨便當或麻辣鍋？</button>
                        <button class="prompt-chip" onclick="sendQuickPrompt('現在趕時間，附近 7-11 或全家便利商店有什麼符合我健康限制的鮮食？')">🏪 推薦附近 7-11 / 全家超商合規鮮食</button>
                        <button class="prompt-chip" onclick="sendQuickPrompt('我覺得上一餐太油太重鹹了，請幫我調高清淡偏好並重新推薦！')">🥗 覺得太油了，幫我換清淡一點的選擇</button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Bottom ChatGPT Input Bar -->
        <div class="input-dock">
            <div class="input-box-wrapper">
                <textarea id="chatInput" rows="1" placeholder="像跟 ChatGPT 聊天一樣輸入需求（例如：晚餐在公館想吃清淡一點的高蛋白便當，我不吃花生）..." onkeydown="handleKeyDown(event)"></textarea>
                <button class="btn-send" onclick="sendChatMessage()" title="送出訊息">➤</button>
            </div>
            <div class="disclaimer-foot">
                NutriAgent 提供一般外食營養決策輔助，非醫療器材亦不取代醫師或臨床營養師診斷。所有推薦均經過確定性臨床硬閘門與資料庫數值一致性驗證。
            </div>
        </div>
    </main>

    <script>
        const profiles = {{ profiles | tojson }};
        const ALLERGEN_KEYS = [
            "seafood", "crustacean", "fish", "peanuts", "tree_nuts",
            "gluten", "dairy", "egg", "soy", "sesame", "mango", "sulfites"
        ];

        function updateProfileView() {
            const selId = document.getElementById("userSelect").value;
            const p = profiles[selId];
            const m = p.metrics;
            const allgList = p.allergens || [];

            ALLERGEN_KEYS.forEach(k => {
                const el = document.getElementById("allg_" + k);
                if (el) el.checked = allgList.includes(k);
            });

            document.getElementById("profileDesc").innerText = p.description;
            document.getElementById("profileMetrics").innerHTML = `
                <div class="metric-chip"><span>血壓</span><span class="${m.blood_pressure_systolic >= 130 ? 'val-danger' : 'val-safe'}">${m.blood_pressure_systolic}/${m.blood_pressure_diastolic}</span></div>
                <div class="metric-chip"><span>空腹血糖</span><span class="${m.fasting_glucose_mg_dl >= 100 ? 'val-danger' : 'val-safe'}">${m.fasting_glucose_mg_dl} mg/dL</span></div>
                <div class="metric-chip"><span>血尿酸</span><span class="${m.uric_acid_mg_dl >= 7.0 ? 'val-danger' : 'val-safe'}">${m.uric_acid_mg_dl} mg/dL</span></div>
                <div class="metric-chip"><span>LDL 膽固醇</span><span class="${m.ldl_c_mg_dl >= 130 ? 'val-warning' : 'val-safe'}">${m.ldl_c_mg_dl} mg/dL</span></div>
            `;
        }

        function getCheckedAllergens() {
            const checked = [];
            ALLERGEN_KEYS.forEach(k => {
                const el = document.getElementById("allg_" + k);
                if (el && el.checked) checked.push(k);
            });
            return checked;
        }

        function formatMarkdown(text) {
            if (!text) return "";
            let html = text
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;");
            html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
            html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
            html = html.replace(/`(.*?)`/g, '<code>$1</code>');
            html = html.replace(/^- (.*$)/gim, '<li>$1</li>');
            html = html.replace(/(<li>.*<\/li>)/gim, '<ul>$1</ul>');
            html = html.replace(/<\/ul>\s*<ul>/g, '');
            html = html.replace(/\n/g, '<br/>');
            return `<div class="md-content">${html}</div>`;
        }

        function handleKeyDown(e) {
            if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                sendChatMessage();
            }
        }

        function sendQuickPrompt(text) {
            const input = document.getElementById("chatInput");
            input.value = text;
            sendChatMessage();
        }

        function appendUserBubble(text) {
            const stream = document.getElementById("chatStream");
            const div = document.createElement("div");
            div.className = "msg-row user";
            div.innerHTML = `
                <div class="avatar user">👤</div>
                <div class="msg-bubble">${text.replace(/</g, "&lt;")}</div>
            `;
            stream.appendChild(div);
            stream.scrollTop = stream.scrollHeight;
        }

        function appendLoadingBubble() {
            const stream = document.getElementById("chatStream");
            const div = document.createElement("div");
            div.className = "msg-row agent";
            div.id = "loadingBubble";
            div.innerHTML = `
                <div class="avatar agent">🥗</div>
                <div class="msg-bubble" style="color: #94a3b8;">
                    ⏳ NutriAgent 正在同步穿戴式 IoT 代謝數據、執行臨床/過敏硬閘門篩選與 Gemini 語義推論...
                </div>
            `;
            stream.appendChild(div);
            stream.scrollTop = stream.scrollHeight;
        }

        function removeLoadingBubble() {
            const el = document.getElementById("loadingBubble");
            if (el) el.remove();
        }

        async function sendChatMessage() {
            const input = document.getElementById("chatInput");
            const msg = input.value.trim();
            if (!msg) return;
            input.value = "";

            appendUserBubble(msg);
            appendLoadingBubble();

            const selId = document.getElementById("userSelect").value;
            const activity = document.getElementById("activityPreset").value;
            const mealType = document.getElementById("mealType").value;
            const locCoords = document.getElementById("locationSelect").value.split(",");

            try {
                const res = await fetch("/api/chat", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({
                        message: msg,
                        profile_id: selId,
                        activity_preset: activity,
                        meal_type: mealType,
                        lat: parseFloat(locCoords[0]),
                        lon: parseFloat(locCoords[1]),
                        allergens: getCheckedAllergens()
                    })
                });
                const data = await res.json();
                removeLoadingBubble();
                renderAgentChatResponse(data);
            } catch (err) {
                removeLoadingBubble();
                alert("對話請求失敗: " + err);
            }
        }

        function renderAgentChatResponse(data) {
            // Update Top Bar & Sidebar Weights
            if (data.metabolic_budget) {
                document.getElementById("statTDEE").innerText = data.metabolic_budget.dynamic_tdee_kcal + " kcal";
                document.getElementById("statBudget").innerText = data.metabolic_budget.target_meal_calories + " kcal";
            }
            if (data.spatial_context) {
                document.getElementById("statSafe").innerText = data.spatial_context.safe_candidates_count + " 道";
                document.getElementById("statRejected").innerText = data.spatial_context.clinical_rejected_count + " 道";
            }
            if (data.drl_flavor_weights) {
                document.getElementById("weightClean").innerText = data.drl_flavor_weights.light_clean.toFixed(3);
                document.getElementById("weightSavory").innerText = data.drl_flavor_weights.bento_savory.toFixed(3);
                document.getElementById("weightProtein").innerText = data.drl_flavor_weights.high_protein.toFixed(3);
            }

            // Build Reasoning Trace HTML
            let traceHtml = "";
            if (data.reasoning_trace && data.reasoning_trace.length > 0) {
                const steps = data.reasoning_trace.map(s => `<div class="trace-step">${formatMarkdown(s)}</div>`).join("");
                traceHtml = `
                    <details class="trace-box">
                        <summary>🧠 檢視 NutriAgent 8 階段臨床推理與安全閘門軌跡 (${data.reasoning_trace.length} 步驟)</summary>
                        ${steps}
                    </details>
                `;
            }

            // Build Interactive Top-3 Cards HTML
            let cardsHtml = "";
            if (data.recommendations && data.recommendations.length > 0) {
                const cardItems = data.recommendations.map((m, idx) => {
                    const rClass = idx === 0 ? "rank-1" : (idx === 1 ? "rank-2" : "rank-3");
                    return `
                        <div class="chat-meal-card">
                            <div>
                                <div class="card-badge-row">
                                    <span class="rank-tag ${rClass}">Top ${m.rank} 推薦</span>
                                    <span style="font-size: 11px; color: #6ee7b7;">🛡️ 臨床/過敏合規</span>
                                </div>
                                <div style="font-weight: 700; font-size: 14.5px; color: #f8fafc;">${m.dish_name}</div>
                                <div style="font-size: 11.5px; color: var(--text-sub); margin-top: 2px;">
                                    🏪 ${m.store_name} · 🚶 ${m.distance_km}km (${m.walking_time_min}分) · NT$${m.price_twd}
                                </div>
                                <div class="nutri-mini-grid">
                                    <div><div class="n-lbl">熱量</div><div class="n-val" style="color:#38bdf8;">${m.calories_kcal}</div></div>
                                    <div><div class="n-lbl">蛋白質</div><div class="n-val">${m.protein_g}g</div></div>
                                    <div><div class="n-lbl">脂肪</div><div class="n-val">${m.fat_g}g</div></div>
                                    <div><div class="n-lbl">鈉含量</div><div class="n-val" style="color:#34d399;">${m.sodium_mg}mg</div></div>
                                </div>
                            </div>
                            <div class="card-btn-row">
                                <button class="card-btn c-accept" onclick="triggerCardFeedback('${m.meal_id}', '${m.dish_name}', 'accept')">✔️ 採納</button>
                                <button class="card-btn c-oily" onclick="triggerCardFeedback('${m.meal_id}', '${m.dish_name}', 'too_oily')">🍳 太油/太鹹</button>
                                <button class="card-btn c-skip" onclick="triggerCardFeedback('${m.meal_id}', '${m.dish_name}', 'skip')">⏭️ 換別家</button>
                            </div>
                        </div>
                    `;
                }).join("");
                cardsHtml = `<div class="chat-cards-grid">${cardItems}</div>`;
            }

            const stream = document.getElementById("chatStream");
            const div = document.createElement("div");
            div.className = "msg-row agent";
            div.innerHTML = `
                <div class="avatar agent">🥗</div>
                <div class="msg-bubble">
                    ${traceHtml}
                    ${formatMarkdown(data.reply)}
                    ${cardsHtml}
                </div>
            `;
            stream.appendChild(div);
            stream.scrollTop = stream.scrollHeight;
        }

        async function triggerCardFeedback(mealId, dishName, feedbackType) {
            const labelMap = {
                "accept": `我決定採納【${dishName}】！`,
                "too_oily": `我覺得【${dishName}】看起來太油太鹹了，請幫我調高清淡健康偏好並重推！`,
                "skip": `我想跳過【${dishName}】，換別家看看。`
            };
            appendUserBubble(labelMap[feedbackType]);

            try {
                await fetch("/api/feedback", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({ meal_id: mealId, feedback_type: feedbackType })
                });
                // Follow up with conversational re-ranking
                document.getElementById("chatInput").value = labelMap[feedbackType];
                // Directly invoke /api/chat without duplicating user bubble
                appendLoadingBubble();
                const selId = document.getElementById("userSelect").value;
                const activity = document.getElementById("activityPreset").value;
                const mealType = document.getElementById("mealType").value;
                const locCoords = document.getElementById("locationSelect").value.split(",");
                document.getElementById("chatInput").value = "";

                const res = await fetch("/api/chat", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({
                        message: labelMap[feedbackType],
                        profile_id: selId,
                        activity_preset: activity,
                        meal_type: mealType,
                        lat: parseFloat(locCoords[0]),
                        lon: parseFloat(locCoords[1]),
                        allergens: getCheckedAllergens()
                    })
                });
                const data = await res.json();
                removeLoadingBubble();
                renderAgentChatResponse(data);
            } catch (err) {
                removeLoadingBubble();
                alert("回饋失敗: " + err);
            }
        }

        async function saveApiKey() {
            const key = document.getElementById("geminiApiKey").value.trim();
            const model = document.getElementById("geminiModel").value;
            try {
                const res = await fetch("/api/config", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({ api_key: key, model_name: model })
                });
                const data = await res.json();
                const badge = document.getElementById("geminiStatusBadge");
                if (data.gemini_configured) {
                    badge.className = "status-pill status-online";
                    badge.innerText = "🟢 Gemini 已連線";
                } else {
                    badge.className = "status-pill status-local";
                    badge.innerText = "⚡ 內建接地引擎";
                }
            } catch (err) {
                console.error(err);
            }
        }

        async function resetConversation() {
            await fetch("/api/config", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({ reset_chat: true })
            });
            location.reload();
        }

        window.onload = updateProfileView;
    </script>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(
        HTML_TEMPLATE,
        profiles=PROFILES,
        gemini_configured=agent.drl.is_gemini_configured
    )


@app.route("/api/config", methods=["POST"])
def api_config():
    data = request.get_json() or {}
    if data.get("reset_chat"):
        agent.clear_conversation()
    if "api_key" in data or "model_name" in data:
        agent.set_gemini_api_key(
            api_key=data.get("api_key", agent.drl.api_key),
            model_name=data.get("model_name", agent.drl.model_name)
        )
    return jsonify({
        "status": "success",
        "gemini_configured": agent.drl.is_gemini_configured,
        "gemini_model": agent.drl.model_name
    })


@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json() or {}
    user_message = data.get("message", "請幫我推薦適合的餐點")
    profile_id = data.get("profile_id", "P_001_HYPERTENSION")
    user_profile = PROFILES.get(profile_id, PROFILES["P_001_HYPERTENSION"])

    lat = float(data.get("lat", 25.0135))
    lon = float(data.get("lon", 121.5342))
    activity_preset = data.get("activity_preset", "moderate")
    meal_type = data.get("meal_type", "lunch")
    custom_allergens = data.get("allergens", None)

    result = agent.chat(
        user_message=user_message,
        user_profile=user_profile,
        user_lat=lat,
        user_lon=lon,
        activity_preset=activity_preset,
        meal_type=meal_type,
        custom_allergens=custom_allergens
    )
    return jsonify(result)


@app.route("/api/recommend", methods=["POST"])
def api_recommend():
    data = request.get_json() or {}
    profile_id = data.get("profile_id", "P_001_HYPERTENSION")
    user_profile = PROFILES.get(profile_id, PROFILES["P_001_HYPERTENSION"])

    lat = float(data.get("lat", 25.0135))
    lon = float(data.get("lon", 121.5342))
    activity_preset = data.get("activity_preset", "moderate")
    meal_type = data.get("meal_type", "lunch")
    custom_allergens = data.get("allergens", None)

    result = agent.run_recommendation(
        user_profile=user_profile,
        user_lat=lat,
        user_lon=lon,
        activity_preset=activity_preset,
        meal_type=meal_type,
        custom_allergens=custom_allergens
    )
    return jsonify(result)


@app.route("/api/feedback", methods=["POST"])
def api_feedback():
    data = request.get_json() or {}
    meal_id = data.get("meal_id", "")
    feedback_type = data.get("feedback_type", "skip")

    res = agent.handle_user_feedback(meal_id, feedback_type)
    return jsonify(res)


if __name__ == "__main__":
    print("=" * 70)
    print("🚀 Starting NutriAgent Conversational AI Server (Gemini API + Clinical Gate)")
    print("👉 Open your browser at: http://127.0.0.1:5000")
    print("=" * 70)
    app.run(host="127.0.0.1", port=5000, debug=False)
