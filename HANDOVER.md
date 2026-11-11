# NutriAgent 專題交接與 AI Agent 跨電腦續行開發指南 (HANDOVER.md)

> **交接標準**：*依據課程規範與 OpenSpec 協議，即使原開發者不在，下一位人類開發者或 AI Coding Agent（Antigravity、Cursor、Claude Code、Cline、Copilot）仍能透過本文件與 `AGENTS.md` 在 3 分鐘內理解現況、100% 重現執行、通過所有驗證，並無縫接續下一階段開發。*

---

## 1. 目前專案版本與最新進度摘要 (Current Status: v2.0)

本專案已完成 **`openspec/changes/gemini-chat-agent-v2`** 升級，核心狀態如下：
1. **100% 對齊新版 [`NutriAgent_Proposal.docx`](file:///c:/Users/User/Desktop/物聯網應用與資料分析/FinalProject/NutriAgent_Proposal.docx) 演算法規範 (Algorithm 1–3)**：
   - **穿戴式 IoT 跨感測器合理性檢查 (`plausibility_check`)**：自動比對步數與平均心率，識破並修正「手機放車架震動步數暴增但心率維持靜止」之偽訊號，並支援穿戴資料逾時降級旗標 (`low_confidence = True`)。
   - **動態 TDEE 與單餐上限**：採用 Mifflin-St Jeor 公式計算 BMR，活動熱量乘以 `0.65` 阻尼係數，並強制執行單餐 `900 kcal` 生理吸收上限。
   - **確定性臨床硬閘門與「安全池為空絕不放寬規則」**：涵蓋 2025 AHA/ACC 高血壓（單餐鈉 $\le 700\text{ mg}$ 且非油炸）、ADA 2026 糖尿病前期（排除高 GI 與添加糖 $> 5\text{ g}$）、2020 ACR 痛風（排除高普林）、高血脂（飽和脂肪 $\le 5\text{ g}$）、慢性腎臟病 CKD（`eGFR < 60` 排除高鉀高磷）與 **衛福部 TFDA 11 類強制過敏原**。當安全候選池為空時，絕不放寬醫療規則，改回傳 `status="no_compliant_meal"` 與定製化點餐減害建議 (`order_tips`)。
   - **數值接地一致性檢查 (`verify_explanation_consistency`)**：確保推薦理由中的所有熱量、蛋白質、鈉含量數值 100% 來自資料庫，杜絕語言模型數值幻覺。
2. **以 Google Gemini API 取代 PyTorch 深度神經網路 (`src/recommender.py`)**：
   - 移除沉重的 PyTorch 神經網路依賴，改為實作 `GeminiRecommender`（保留 `DRLRecommender` 相容別名）。
   - 支援串接 `gemini-2.5-flash` / `gemini-2.0-flash` / `gemini-1.5-pro` 進行自然語言意圖解析、語義渴望評分、線上偏好權重更新（`w = [清淡健康, 傳統便當, 高蛋白]`）與接地臨床衛教對話生成。
   - **免金鑰離線備援**：未設定 `GEMINI_API_KEY` 時，系統自動切換為內建的確定性臨床語義推論引擎，確保在任何測試環境、助教電腦或無網路環境下皆可毫秒級（`0.21 ms`）執行。
3. **ChatGPT 風格多輪對談式 AI Agent 介面 (`app.py`)**：
   - 支援自然語言多輪對話、快捷提問晶片（Prompt Chips）、可展開的 **8 階段臨床推理軌跡 (Reasoning Trace)**，以及對話串內嵌的 **Top-3 互動推薦卡片**（可直接點擊「✔️ 採納」、「🍳 太油/太鹹」、「⏭️ 換別家」或用文字對話即時調整偏好權重）。

---

## 2. 跨電腦零障礙啟動清單 (Quick Start on Any Machine)

### 步驟 1：安裝輕量化依賴套件
本專案已移除龐大的 PyTorch 依賴，僅需標準科學計算與 Web 套件（`numpy`、`Flask`、`python-docx`）：
```bash
pip install -r requirements.txt
```

### 步驟 2：設定 Gemini API Key（選填）
您有兩種方式設定 Google Gemini API Key（若不設定，系統亦可使用內建臨床語義推論引擎完整運行）：
1. **網頁介面即時輸入（推薦）**：啟動 `python app.py` 後，直接在網頁左側邊欄「✨ Gemini API 引擎設定」輸入 `AIzaSy...` 金鑰並點擊「套用」。
2. **環境變數設定**：
   ```powershell
   # Windows PowerShell
   $env:GEMINI_API_KEY="您的_GEMINI_API_KEY"
   python app.py
   ```

### 步驟 3：一鍵執行與驗證指令

| 任務目標 | 執行指令 | 預期結果 |
| :--- | :--- | :--- |
| **1. 自動化單元測試 (9 項測試)** | `python -m unittest tests/test_agent.py` | `Ran 9 tests ... OK` |
| **2. 客觀 KPI 基準評測** | `python benchmark.py` | `CVR: 0.0%`, `AVR: 0.0%`, `MAE: 114.48 kcal`, `PASSED` |
| **3. 終端機多輪對談示範** | `python demo_run.py` | 完整印出 Turn 1 推薦與 Turn 2「太油」回饋更新 |
| **4. 啟動 ChatGPT 風格網頁介面** | `python app.py` | 瀏覽器開啟 `http://127.0.0.1:5000` 開始對話 |

---

## 3. 模組職責與架構導覽 (Codebase Ownership Map)

```
FinalProject/
├── AGENTS.md                        # 【AI Agent 協同開發憲章】供後續 AI Agent 讀取的規格與優化路線圖
├── HANDOVER.md                      # 【本文件】跨電腦交接與擴充指南
├── NutriAgent_Proposal.docx         # 【新版正式提案書 Word 檔】Algorithm 1–3 與文獻唯一真實來源
├── PROPOSAL.md & DESIGN.md          # 【Markdown 規格書】與 DOCX 同步之架構與演算法文件
├── src/
│   ├── clinical_rules.py            # 【臨床營養與 TFDA-11 過敏硬閘門】
│   │                                #  evaluate_meal_safety(), filter_safe_candidates(), generate_order_tips()
│   ├── iot_pipeline.py              # 【穿戴式 IoT 轉接器與動態代謝管線】
│   │                                #  plausibility_check(), static_estimate(), calculate_dynamic_budget() (含 900kcal 上限)
│   ├── spatial_lbs.py               # 【地理空間檢索】Haversine 距離計算與 1.2km -> 2.5km 自動擴展
│   ├── recommender.py               # 【Gemini API 語義推薦與線上偏好引擎】
│   │                                #  GeminiRecommender (別名 DRLRecommender)，負責 NLU、偏好權重更新與接地回覆生成
│   └── agent.py                     # 【中央代理人協同中樞】
│                                    #  NutriAgent.run_recommendation(), NutriAgent.chat(), verify_explanation_consistency()
├── data/
│   ├── sample_health_reports.json   # 5 組臨床測試表型 (高血壓、糖尿病前期、痛風、運動員、久坐學生)
│   └── meal_catalog.json            # 台灣超商與連鎖餐飲營養與過敏原資料庫
├── openspec/                        # 【OpenSpec 規格驅動開發目錄】
│   ├── specs/                       #  各模組永久規格契約
│   └── changes/gemini-chat-agent-v2/#  本次 v2.0 升級之完整提案、設計與任務清單
├── tests/
│   └── test_agent.py                # 9 項自動化測試 (涵蓋臨床零違規、TFDA-11 過敏原、震動偽訊號、空池不放寬、對話 Agent)
├── app.py                           # Flask ChatGPT 風格對談式 Web 伺服器
└── benchmark.py                     # 機器可讀 KPI 評測腳本
```

---

## 4. 接手開發者 / 後續 AI Agent 擴充指南 (Extension Playbook)

### 情境 A：如何讓下一個 AI Agent 接手開發？
只需對您的 AI 編碼助手（如 Antigravity / Cursor / Claude Code）下達以下指令：
> *「請先閱讀 `AGENTS.md`、`HANDOVER.md` 與 `openspec/changes/gemini-chat-agent-v2/`，執行 `python benchmark.py` 與 `python -m unittest tests/test_agent.py` 確認環境正常，接著幫我實作 `AGENTS.md` 中的 Track 1（或您指定的功能）。」*

### 情境 B：如何擴充新的對談意圖或 Gemini 提示詞？
1. 打開 [`src/recommender.py`](file:///c:/Users/User/Desktop/物聯網應用與資料分析/FinalProject/src/recommender.py)。
2. 在 `parse_conversation_intent()` 中可擴充新的自然語言關鍵字或情境欄位。
3. 在 `generate_conversational_reply()` 中可調整 `system_inst`（系統提示詞），但請務必保留「所有營養數字必須 100% 引用 JSON 資料庫欄位」之約束，以通過 `src/agent.py` 中的 `verify_explanation_consistency()` 檢查。

### 情境 C：如何新增臨床規則或餐點資料？
* **新增臨床規則**：於 [`src/clinical_rules.py`](file:///c:/Users/User/Desktop/物聯網應用與資料分析/FinalProject/src/clinical_rules.py) 的 `evaluate_meal_safety()` 加入條件，並在 `generate_order_tips()` 補上對應的點餐調整建議。
* **新增餐點資料**：於 [`data/meal_catalog.json`](file:///c:/Users/User/Desktop/物聯網應用與資料分析/FinalProject/data/meal_catalog.json) 新增 JSON 物件（過敏原請對齊 `crustacean`, `fish`, `peanuts`, `tree_nuts`, `gluten`, `dairy`, `egg`, `soy`, `sesame`, `mango`, `sulfites`）。
