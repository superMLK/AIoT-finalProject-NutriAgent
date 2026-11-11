# Proposal Document：NutriAgent
## 結合穿戴式 IoT 與臨床營養規則之即時外食決策代理人
### A Real-Time Dietary Decision Agent Integrating Wearable IoT Telemetry and Clinical Nutrition Rules

**課程**：物聯網應用與資料分析（IoT Applications and Data Analysis）  
**專題類型**：Domain AI Agent：`AI Agent + Domain Knowledge + Data Analytics + Real-World Application`  
**日期**：2026 年 11 月  

---

## 1. Abstract 摘要

* **A. Attention Getter — Motivation**  
  外食已是台灣多數成人的日常。2025 年 11 月台灣營養基金會等單位針對 1,000 名 22–65 歲上班族的調查顯示，近七成國人有外食習慣，超過四成上班族天天外食 [18]；國民健康署調查則指出，20 歲以上國人約每 10 人就有 3 人符合代謝症候群 [17]。放大到全球，WHO《Global Report on Hypertension 2025》估計 2024 年有 14 億人罹患高血壓，獲得控制者僅略高於五分之一 [15]。外食族每天都要在「附近買得到什麼」和「健檢紅字不能吃什麼」之間做決定。
* **B. But — Challenge**  
  現有工具各缺一角。飲食記錄 App 只能事後記帳，無法在使用者站在店門口時給建議。單純無接地的通用大型語言模型（LLM）雖能對話，但 2025 年一項以台灣 7-Eleven 即食便當為樣本的研究發現，五款聊天機器人普遍低估鈉含量，重複詢問的變異係數高達 20–70% [5]。學術界的健康感知推薦系統（如 KDD 2025 的 MOPI-HFRS [1] 與 MORL-A2C [2]）把「健康」當成可以和口味互相交換的軟性目標，且多為離線推薦，不考慮使用者當下的位置與活動量。穿戴裝置的活動熱量估算誤差普遍超過 30% [10]，若一比一拿來補償飲食反而有風險。  
  **Research Gap**：目前缺少一個能同時整合即時活動資料、健檢硬約束與實體可購餐點，並在保證安全的前提下做個人化排序與自然語言互動的外食決策 Agent。
* **C. Cure — Proposed Solution**  
  為了解決上述問題，本專題提出 **NutriAgent**：一個結合臨床營養規則、穿戴式 IoT 資料與 **Google Gemini API 對談式智慧代理人** 的外食推薦 Domain AI Agent。它先依健檢指標與過敏原強制排除不能吃的餐點，再結合個人化偏好與 Gemini 語義推理從步行可達的超商與便當店中挑出最適合的 Top-3，以類似 ChatGPT 的自然語言對話呈現推薦理由；使用者的對話回饋會即時改變下一次的排序。
* **D. Development — Method**  
  NutriAgent 以 Planner 協調 8 階段管線：
  1. **IoT Adapter** 取得步數與活動熱量（對接 Android Health Connect／Apple HealthKit，原型含活動模擬器與跨感測器合理性檢查 `plausibility_check`），以 Mifflin-St Jeor 公式 [22] 計算 BMR，加上乘以 0.65 阻尼係數的活動熱量得到動態 TDEE，並設單餐上限 900 kcal；
  2. 以 **Haversine 距離** 檢索 1.2 km 內的餐點，不足 4 筆時自動擴大到 2.5 km；
  3. **確定性臨床閘門** 依 2025 AHA/ACC 高血壓指引 [12]、ADA 2026 照護標準 [13]、2020 ACR 痛風指引 [14] 與 TFDA 11 類過敏原 [16] 排除禁忌餐點（當安全候選池為空時絕不放寬規則，改回報 `NO_COMPLIANT_MEAL` 與點餐調整建議）；
  4. **Gemini API 語義與情境偏好排序引擎** 結合線上口味偏好權重（清淡、傳統便當、高蛋白）與營養契合度、距離加權成綜合分數；
  5. 產生 **100% 引用資料庫數值** 的臨床理由（通過 `assert numbers_in(E) == db_values(R)` 一致性檢查），並透過 ChatGPT 風格對話介面支援多輪問答與「採納／太油／跳過」線上偏好更新。
* **E. Experiments — Evaluation**  
  實驗評估臨床禁忌違規率（CVR = 0%）、過敏原違規率（AVR = 0%）、熱量目標平均絕對誤差（MAE ≤ 180 kcal）、推論延遲與口味偏好收斂速度。

---

## 2. Proposed Scheme 系統設計與核心演算法

### 2.1 模組對應表
| 模組 | 功能說明 | 主要輸出 | 原型對應檔案 |
| :--- | :--- | :--- | :--- |
| **① User / Scenario** | 外食族在早/午/晚餐時段、位於某商圈，透過類似 ChatGPT 的對話介面提出飲食需求。 | 使用者身分、對話訊息、時段、商圈 | `app.py`、`demo_run.py` |
| **② Query / Input** | 收集健檢指標（血壓、空腹血糖、尿酸、LDL-C、eGFR）、TFDA 11 類過敏原、GPS 與穿戴活動狀態。 | 結構化使用者檔案與自然語言查詢 | `data/sample_health_reports.json` |
| **③ Planner & Reasoning Agent** | NutriAgent 中樞：解析自然語言意圖、依序調度工具、處理例外（穿戴失敗降級、候選不足擴展半徑、安全池為空不放寬規則）。 | 執行計畫與 8 階段推理軌跡 (Reasoning Trace) | `src/agent.py` |
| **④ Data Acquisition / Retrieval** | IoT Adapter 取得步數與心率並執行合理性檢查；Haversine 檢索 1.2 km → 2.5 km 餐點。 | 候選餐點＋距離與步行時間 | `src/iot_pipeline.py`、`src/spatial_lbs.py` |
| **⑤ Analytics Engine** | BMR (Mifflin-St Jeor) + 0.65 × 活動熱量 = 動態 TDEE（單餐上限 900 kcal）；情境狀態編碼 $s_t$。 | 當餐預算、狀態向量 $s_t$ | `src/iot_pipeline.py`、`src/recommender.py` |
| **⑥ Domain Knowledge Integration** | 確定性臨床硬約束閘門與 TFDA 11 類過敏原別名比對，逐筆判斷並記錄違規原因。 | 安全候選池 $S$＋排除原因 $V$ | `src/clinical_rules.py` |
| **⑦ Decision / Recommendation** | Gemini API 結合線上偏好權重評估每個安全餐點，與營養契合度、距離加權取 Top-3 並生成數值接地之臨床理由。 | Top-3 推薦＋臨床解釋 | `src/recommender.py`、`src/agent.py` |
| **⑧ Output & Conversational UI** | ChatGPT 風格對話串呈現推理軌跡、自然語言回覆與互動卡片；回饋即時更新偏好權重。 | 多輪對話回覆、更新後偏好權重 | `app.py` (`/api/chat`, `/api/feedback`) |

---

### 2.2 Pseudocode 核心演算法

```text
Algorithm 1: NutriAgent Real-Time Conversational Dietary Decision Agent
Input : profile U, health metrics H, allergens A, location L, meal type t,
        wearable stream W, user chat message M, Gemini Recommender G
Output: Conversational reply Reply, Top-3 recommendations R with clinical explanations E
01: receive request (U, H, A, L, t, M)
02: try: telemetry <- IoTAdapter.fetch(W)        # Health Connect / simulator
03: catch timeout/denied: telemetry <- static_estimate(U); flag LOW_CONF
04: telemetry <- plausibility_check(telemetry)   # steps vs heart rate artifact filter
05: BMR <- MifflinStJeor(U.sex, U.weight, U.height, U.age)
06: TDEE <- BMR + 0.65 * telemetry.active_kcal   # damp wearable error
07: budget <- min(TDEE * ratio[t], 900); macros <- split(budget, H)
08: C <- LBS.retrieve(L, radius = 1.2 km)
09: if |C| < 4 then C <- LBS.retrieve(L, radius = 2.5 km)
10: S <- ClinicalGate(C, H, A)                    # Algorithm 2
11: if S is empty then
12:     return NO_COMPLIANT_MEAL, order_tips(C, H)   # never relax rules
13: s_t <- encode_state(t, budget, steps, H, pref_w)   # 8-dim state
14: for each meal m in S do
15:     a_m <- encode_action(m)                   # 6-dim nutrition/flavor
16:     q <- G.score_preference(s_t, a_m, m, M)   # Gemini semantic + preference score
17:     fit <- 1 - (0.6 * calorie_error + 0.4 * protein_error)
18:     m.score <- 0.50 * q + 0.35 * fit - 0.15 * min(1, m.distance / 1.5)
19: R <- top_k(S, by = score, k = 3)
20: E <- explain(R, H, budget)                    # numbers copied from DB fields only
21: assert numbers_in(E) == db_values(R)          # consistency check
22: Reply <- G.generate_conversational_reply(M, U, R, E)
23: present(Reply, R, E); return Reply, R, E
```
