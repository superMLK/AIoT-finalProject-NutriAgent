# OpenSpec Change Proposal: 同步新版 Proposal、串接 Gemini API 取代神經網路與 ChatGPT 對話式 UI 升級
Change ID: `gemini-chat-agent-v2`

## 1. Why & Motivation
1. **同步最新 `NutriAgent_Proposal.docx` 規範**：
   - 最新版 Proposal 明確定義了 Algorithm 1–3：包含穿戴式裝置跨感測器合理性檢查 (`plausibility_check`)、單餐 900 kcal 消化吸收上限、TFDA 11 大類強制過敏原標示對齊、安全候選池為空時「絕不放寬臨床規則 (`NO_COMPLIANT_MEAL` + 點餐調整建議 `order_tips`)」，以及解釋文字之數值一致性檢查 (`numbers_in(E) == db_values(R)`)。
2. **以 Gemini API 取代本地 PyTorch 深度神經網路**：
   - 移除原本的 PyTorch `NutriQNetwork` 深度強化學習神經網路，改為串接 **Google Gemini API** (`gemini-2.5-flash` / `gemini-2.0-flash`) 進行自然語言意圖解析、個人化口味偏好推理與具備資料庫數值接地 (Grounded) 的臨床衛教對話生成，並保留結構化口味偏好權重記憶 (`user_flavor_weights`) 與離線快速推論備援。
3. **升級為類似 ChatGPT 之對話式 Agent 介面 (Conversational UI)**：
   - 原本的單向表單介面改版為類似 ChatGPT 的多輪對話式 Agent 介面，使用者可直接用自然語言（例如：「今天中午在公館想吃清淡一點的高蛋白便當」、「覺得太油了換一家」、「為什麼我不能吃排骨便當？」）與 NutriAgent 對話，並在對話串中即時呈現 Agent 推理步驟 (Reasoning Trace) 與互動式餐點推薦卡片。

## 2. What (Proposed Changes)
* **`src/clinical_rules.py`**：
  - 擴充過敏原別名表對齊衛福部 **TFDA 11 類過敏原**（甲殼類、芒果、花生、牛奶/羊奶、蛋、堅果類、芝麻、含麩質之穀物、大豆、魚類、亞硫酸鹽類，並向下相容 `seafood` 綜合類別）。
  - 新增慢性腎臟病 (CKD, `eGFR < 60`) 高鉀高磷攔截規則。
  - 新增 `generate_order_tips()`，當安全候選池為空時提供不放寬臨床邊界的定製化點餐減害建議。
* **`src/iot_pipeline.py`**：
  - 實作 `plausibility_check()`（比對步數與平均心率以過濾行車震動假步數）與 API 失敗降級旗標 (`low_confidence`)。
  - 實作單餐熱量上限 `min(TDEE * ratio[t], 900.0)`。
* **`src/recommender.py`**：
  - 移除 PyTorch 神經網路 (`torch.nn`)，改為實作 `GeminiRecommender`，串接 Google Gemini API 進行語義偏好評分、對話意圖抽取與推薦理由生成，並支援即時回饋權重更新 (`accept` / `too_oily` / `skip`)。
* **`src/agent.py`**：
  - 修正安全候選池為空時的行為：嚴格遵守「不放寬規則 (`NO_COMPLIANT_MEAL`)」，回傳 `order_tips`。
  - 新增數值一致性檢查 (`verify_numerical_consistency`)，確保輸出之熱量、蛋白質、鈉含量與資料庫 100% 一致。
  - 新增 `chat()` 多輪對話方法，整合工具調用軌跡與對話歷史。
* **`app.py`**：
  - 全面改版為 ChatGPT 風格之深色玻璃擬態對話式 Agent 介面，支援自然語言對話、快捷提問晶片、Agent 思考過程展開、即時餐點卡片回饋與側邊欄 Gemini API Key / 健檢紅字 / 過敏原設定。
