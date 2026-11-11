# NutriAgent 智動食健 (v2.0)
## 結合穿戴式 IoT、臨床營養硬規則與 Google Gemini API 之即時外食對談決策代理人
### A Real-Time Conversational Dietary Decision Agent Integrating Wearable IoT Telemetry, Clinical Nutrition Rules, and Google Gemini API

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Gemini API](https://img.shields.io/badge/Google%20Gemini-2.5%20Flash-4285F4.svg)](https://ai.google.dev/)
[![Flask](https://img.shields.io/badge/Flask-3.0%2B-green.svg)](https://flask.palletsprojects.com/)
[![OpenSpec](https://img.shields.io/badge/OpenSpec-v1.0%20Compliant-brightgreen.svg)]()

> **課程專題**：「物聯網應用與資料分析 (IoT Applications & Data Analysis)」期末專題  
> **核心範式**：`AI Agent + Domain Knowledge + Data Analytics + Real-World Application`  
> **AI Agent 交接支援**：本儲存庫遵循 **OpenSpec** 規格驅動開發，任何人類開發者或 AI Coding Agent 皆可透過 [`AGENTS.md`](AGENTS.md) 與 [`HANDOVER.md`](HANDOVER.md) 無縫接手。

---

## 📌 專題核心架構與創新 (Key Innovations)

1. **安全與偏好解耦的雙層決策 (Safety-Preference Decoupling)**：
   - **第一層：確定性臨床與過敏原硬閘門 ([`src/clinical_rules.py`](src/clinical_rules.py))** — 依據 **2025 AHA/ACC 高血壓指引**（單餐鈉 $\le 700\text{ mg}$、禁油炸）、**ADA 2026 糖尿病照護標準**（禁高 GI、添加糖 $\le 5\text{ g}$）、**2020 ACR 痛風指引**（禁高普林）、**CKD 腎病變規則**（`eGFR < 60` 限鉀磷）及 **衛福部 TFDA 11 類強制過敏原** 進行 100% 零容忍篩選（`CVR = 0.0%`, `AVR = 0.0%`）。當周邊無合規餐點時**絕不放寬醫療規則**，改回報 `NO_COMPLIANT_MEAL` 與定製化點餐減害建議 (`order_tips`)。
   - **第二層：Google Gemini API 語義與線上偏好排序 ([`src/recommender.py`](src/recommender.py))** — 串接 Google Gemini API 理解使用者自然語言渴望（如「剛運動完想吃清淡高蛋白」），結合線上可解釋口味偏好權重 `w = [清淡健康, 傳統便當, 高蛋白]`、營養契合度與 Haversine 步行距離選出最佳 Top-3。
2. **具備誤差意識與合理性檢查的穿戴式 IoT 代謝預算 ([`src/iot_pipeline.py`](src/iot_pipeline.py))**：
   - 實作跨感測器合理性檢查 (`plausibility_check`)，自動識破「手機放車架震動導致步數暴增但心率維持靜止」之偽訊號；以 Mifflin-St Jeor 公式計算 BMR，搭配 `0.65` 活動熱量阻尼係數與單餐 `900 kcal` 上限計算動態 TDEE。
3. **ChatGPT 風格多輪對談介面與數值接地驗證 ([`app.py`](app.py), [`src/agent.py`](src/agent.py))**：
   - 支援自然語言多輪對話、8 階段推理軌跡展開 (Reasoning Trace)、內嵌互動式推薦卡片與即時回饋學習，並強制執行 `assert numbers_in(E) == db_values(R)` 數值一致性檢查，徹底杜絕 LLM 營養數值幻覺。

---

## 🚀 快速啟動與驗證 (Quick Start)

```powershell
# 1. 安裝依賴套件
pip install -r requirements.txt

# 2. 執行自動化測試套件 (9/9 全數通過)
python -m unittest tests/test_agent.py

# 3. 執行客觀 KPI 基準評測 (CVR=0.0%, AVR=0.0%, MAE=114.48 kcal)
python benchmark.py

# 4. 執行命令列多輪對談示範
python demo_run.py

# 5. 啟動 ChatGPT 風格對談式網頁伺服器
python app.py
# 請開啟瀏覽器前往 http://127.0.0.1:5000
```

---

## 📚 專題核心文件導覽

* **[`NutriAgent_Proposal.docx`](NutriAgent_Proposal.docx)** / **[`PROPOSAL.md`](PROPOSAL.md)**：完整期末專題提案書（含文獻回顧、三大核心深度探討、系統架構圖、流程圖與 Algorithm 1–3 Pseudocode）。
* **[`DESIGN.md`](DESIGN.md)**：v2.0 系統架構與模組規格說明書。
* **[`AGENTS.md`](AGENTS.md)**：AI 代理人協同開發憲章（含不變量鐵則、OpenSpec 流程與後續 Track 1–4 優化路線圖）。
* **[`HANDOVER.md`](HANDOVER.md)**：跨電腦環境架設、Gemini API Key 配置與擴充教學指南。
