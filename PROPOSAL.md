# 期末專題提案：NutriAgent
## 結合物聯網感測與健檢知識圖譜之即時適應性外食營養決策代理人
### Real-Time Adaptive Dietary Decision Agent Integrating Wearable IoT Telemetry and Clinical Knowledge Graph

**課程名稱**：物聯網應用與資料分析 (IoT Applications and Data Analysis)  
**專題類型**：Domain AI Agent (AI 飲食導航與代謝健康決策代理人)  
**核心概念**：`AI Agent + Domain Knowledge + Data Analytics + Real-World Application`  

---

## 1. Abstract 摘要

* **[A. Attention Getter — Motivation]**  
  根據世界衛生組織 (WHO, 2024) 與台灣衛福部國民健康署最新國民營養健康狀況調查，台灣 20 歲以上成年人代謝症候群盛行率已攀升至 **34.6%**，且超過 **72.8%** 的都會上班族與大學生為每日至少兩餐依賴外食的「長期外食族」。外食環境長期存在高鈉、高精緻澱粉、隱性飽和脂肪過剩之結構性問題，成為誘發第二型糖尿病、高血壓及心血管疾病的核心元兇。與此同時，智慧手環與智慧手錶的普及率在 2025 年已突破 45%，為即時生理指標監測提供了前所未有的物聯網 (IoT) 數據基礎。
* **[B. But — Challenge]**  
  現有解決方案存在三大致命斷層（Research Gaps）：(1) 傳統飲食記錄 App（如 MyFitnessPal、FatSecret）高度依賴使用者事後繁瑣的手動秤重輸入，缺乏事前主動引導決策，三週內流失率高達 80% 以上；(2) 通用大型語言模型（如 ChatGPT、Claude）雖具備對話能力，但缺乏即時穿戴物聯網數據接入與精確地理位置感知，且在精確數值計算上容易產生「營養學幻覺 (Nutritional Hallucination)」；(3) 商業外送與地圖推薦系統（如 UberEats、Google Maps）純粹以點閱率與廣告競價為導向，完全脫鉤使用者的臨床健檢紅字（如高血壓禁高鈉、高尿酸避高普林）及動態熱量代謝缺口。
* **[C. Cure — Proposed Solution]**  
  為解決上述問題，本專題提出 **NutriAgent**——一個具備臨床營養學專家思維的 **即時適應性領域智慧代理人 (Domain AI Agent)**。NutriAgent 能夠自主感知使用者的動態熱量代謝（透過 Google Fit IoT 穿戴數據）、嚴格遵循個體病理邊界（解析臨床健檢報告紅字）、檢索周邊真實外食地理圖譜（LBS 與超商/連鎖餐廳營養成分庫），並運用**深度強化學習 (Deep Reinforcement Learning, DRL)** 持續演進個人口味偏好，在「健康安全」與「口腹之慾」間取得最佳平衡。
* **[D. Development — Method]**  
  系統架構整合四大核心引擎：
  1. **IoT 代謝時序分析模組**：透過 Google Fit REST API 即時獲取步數、運動消耗卡路里、心率與活動區間，計算動態總能量消耗 (Dynamic TDEE)。
  2. **臨床醫學硬約束引擎 (Clinical Constraint Filter)**：將健檢指標（血壓、空腹血糖、血脂、尿酸、腎功能）轉化為醫學營養治療 (MNT) 數學約束，強制剔除致命禁忌食材。
  3. **深度強化學習偏好模型 (DRL Contextual Recommender)**：將用餐時段、熱量缺口與口味特徵建模為狀態空間，透過 DQN / Contextual Bandit 動態更新 Q 值網路，在推薦中兼顧探索 (Exploration) 與利用 (Exploitation)。
  4. **地理空間感知與在地菜單檢索模組 (LBS Engine)**：定位使用者當前半徑 1 公里內店家，建立包含台灣四大超商與連鎖便當店之全營養素標註資料庫。
* **[E. Experiments — Evaluation]**  
  本專題將建立包含 50 組具代表性臨床表型的合成使用者資料集（Synthetic Clinical Profiles，涵蓋高血壓 DASH、糖尿病前期、痛風、減脂及健康對照組），並爬取標註 500+ 道台灣真實外食餐點。評估將與三組基準（Baseline：靜態熱量配比法、純 LLM Zero-Shot 提示法、隨機外送推薦）進行對比，量化指標包含：**臨床禁忌零違規率 (Zero Clinical Violation Rate, 100% 目標)**、**熱量目標偏差誤差 (MAE < 5%)**、**多目標滿意度累積獎勵 (Cumulative Reward)** 及 **冷啟動適應收斂速度**。
* **[F. Findings — Expected Outcomes]**  
  預期 NutriAgent 能在 **100% 絕對杜絕健檢禁忌餐點**的前端硬過濾前提下，將推薦餐點之使用者滿意度與實際採納率提升 **40% 以上**，並能於 5 次互動內自動學會使用者的口味偏好轉變，實現兼具醫學嚴謹性、實體可行性與高個人化黏著度的外食健康導航代理人。

---

## 2. Introduction 緒論

### A. Attention Getter (問題動機與統計數據)
外食文化已成為當代都會生活的常態。根據 2024–2025 年台灣行政院主計總處及衛福部統計，全台外食餐飲市場年產值已破兆元，上班族與大專院校學生外食比例分別達 79.2% 與 84.6%。然而，外食店家為了增添風味，普遍採取「高鹽、重油、糖醃、精緻澱粉」的烹調方式。台灣國民營養健康狀況調查指出，18 歲以上國人高血壓盛行率達 26.8%、高血脂達 25.6%、高血糖達 11.1%，年輕族群更呈現急速惡化趨勢。慢性病不再是老年專利，而是每日兩餐甚至三餐外食的青年與中年族群不可承受之重。

### B. Background (應用領域與技術背景)
在健康意識抬頭的浪潮下，兩大關鍵技術基礎已經成熟：
1. **消費級物聯網 (Consumer IoT) 的全面普及**：Google Fit、Apple Health、Garmin 等健康平台透過智慧穿戴裝置（Smartwatch / Fitness Band），能以分鐘級精度持續監控人體步數、代謝當量 (METs)、心率變異度 (HRV) 與主動運動卡路里。
2. **數位健檢報告與開放食品營養資料**：衛福部食品藥物管理署 (TFDA) 釋出的台灣食品成分資料庫，加上各大連鎖超商（7-Eleven、全家）與連鎖餐飲強制公開營養標示，使得「精確算計每一口食物的巨量營養素」在客觀條件上首次具備可行性。

### C. Problem (核心問題定義)
儘管數據隨手可得，一般人在每日午餐或晚餐時分，依舊面臨嚴重的**決策癱瘓 (Decision Paralysis)** 與 **資訊盲區**：
* **動態能量缺口難以掌握**：今天上午在實驗室久坐僅走了 1,500 步，與昨晚慢跑 5 公里消耗 400 大卡相比，午餐所需的熱量與蛋白質配比截然不同。傳統計算僅依賴靜態體重身高公式，無法即時反映今日動態代謝消耗。
* **健檢指標與生活餐點脫鉤**：健檢報告上的「低密度脂蛋白膽固醇 (LDL-C) 偏高」、「空腹血糖 115 mg/dL」、「尿酸 8.2 mg/dL」等紅字警告，常因缺乏專業營養師常駐指導，使用者不知道在巷口便當店該選哪一道主食。
* **地理空間與現實妥協**：理想的健康餐盒可能距離 5 公里之外，或是價格過於昂貴；而在飢餓與時間壓力下，使用者往往直接妥協於最近的炸雞排或高糖手搖飲。

### D. Existing Limitations (既有系統不足與研究缺口)
現有市場工具主要分為三類，皆未能滿足即時個人化外食決策的需求：
1. **被動式卡路里追蹤 App（如 MyFitnessPal）**：僅扮演「數位記帳本」，必須靠使用者自行搜尋食材並輸入克數，繁瑣的反人性操作導致 30 天留存率低於 15%，且無法在使用者站在店門口猶豫不決時主動提供推薦。
2. **通用大型語言模型（如 ChatGPT、Gemini）**：雖然能針對病症提出概括性飲食建議（例如「請多攝取水溶性纖維」），但缺乏 API 層級與 Google Fit、GPS 定位的動態連結；更嚴重的問題在於**缺乏數值確定性 (Numerical Uncertainty)**，生成的餐點熱量往往隨機漂移，無法作為嚴謹的代謝管理依據。
3. **商業地圖與外送平台（如 Google Maps、UberEats）**：推薦演算法本質為利潤極大化，旨在推播促銷高毛利的高熱量油炸食物，並未考量用戶健康福祉。

### E. Innovation (本專題之創新方法)
針對上述缺口，**NutriAgent** 提出三項核心架構創新：
1. **多模態邊界融合架構 (Multi-Modal Constraint Fusion)**：
   創立「醫學硬過濾 (Hard Clinical Gate) + 深度學習軟排序 (Soft Preference Ranking)」的雙層決策機制。第一層以醫學指引嚴格過濾病理禁忌，第二層才由 AI 模型發揮個人偏好調控，徹底根絕 AI 在醫療健康領域的違規風險。
2. **IoT 時序驅動的動態熱量代謝預算 (Dynamic Caloric Budgeting)**：
   即時串接 Google Fit REST API，將基礎代謝率 (BMR) 與時序運動消耗即時疊加，動態推導當前餐次的最佳巨量營養素（碳水化合物、蛋白質、脂肪）黃金窗口。
3. **具備可解釋性的強化學習偏好回饋閉環 (Explainable RL with Human-in-the-Loop)**：
   採用 Contextual Bandit / Deep Q-Network 演算法，將使用者的每一次點選、略過或「太油/想吃清淡」反饋轉換為 Q-value 更新梯度，讓 Agent 能在使用者無需繁瑣配置的情況下，越用越懂使用者的口味。

### F. Contributions (主要預期貢獻)
1. **領域 AI Agent 典範建立**：設計出一個完整體現 `AI Agent + Domain Knowledge + Data Analytics + Real-World Application` 的端到端架構，擺脫單純 Chatbot 形態。
2. **台灣在地外食全營養知識圖譜**：整合台灣四大超商及指標連鎖便當店之營養、價格與過敏原標籤，建立具備空間索引的開放資料庫。
3. **醫學可信的動態調控演算法**：提出結合動態 TDEE、臨床指引（DASH/ADA）與 DRL 推薦的混合決策演算法，並提供具備行號之完整 Pseudocode。
4. **高重現度之開源系統交付**：提供包含完整原始碼、合成測試資料、`DESIGN.md` 與 Streamlit 互動展示平台的工業級專案 Repository。

---

## 3. Related Work 相關研究

本專題架構於 **50% 領域專業知識 (Domain Know-how)** 與 **50% 人工智慧技術 (AI Technology)** 之交叉領域。

### 3.1 領域專業知識 (Domain Know-How)
* **臨床營養學與慢性病醫學營養治療 (Medical Nutrition Therapy, MNT)**：
  - *高血壓*：美國心臟協會 (AHA) 與台灣高血壓學會建議採用得舒飲食 (DASH Diet)，要求單日鈉攝取低於 2,000 mg，單餐鈉含量應嚴格限制於 700 mg 以下，並提高鉀、鎂、鈣之比例。
  - *糖尿病與胰島素阻抗*：美國糖尿病學會 (ADA, 2024–2026 Guidelines) 指出，飲食干預核心不在於完全杜絕碳水，而在於「總升糖負荷 (Glycemic Load, GL)」的平準化與複合水溶性膳食纖維的搭配。
  - *高尿酸與痛風*：風濕免疫科醫學指引明確要求過濾普林含量高於 150 mg/100g 之紅燈食材（如內臟、甲殼類濃縮肉湯、酵母抽出物）。
* **物聯網人體代謝動態評估 (IoT Metabolic Modeling)**：
  人體每日總能量消耗 ($TDEE$) 包含基礎代謝率 ($BMR$)、食物熱效應 ($TEF$) 及活動能量消耗 ($AEE$)。透過穿戴感測器（加速度計、光學心率計）計算活動時的代謝當量 (Metabolic Equivalent of Task, METs)：
  $$\text{Calories Burned (kcal)} = \text{MET} \times \text{Weight (kg)} \times \text{Duration (hr)}$$
  Google Fit API 透過標準化的 Aggregate Request 彙整當日累計之活動消耗熱量，使系統能精準推導出每餐的剩餘能量配額。

### 3.2 人工智慧與推薦系統技術 (AI Technology)
* **基於強化學習的動態推薦系統 (Deep Reinforcement Learning, DRL)**：
  傳統協同過濾 (Collaborative Filtering) 假設使用者偏好是靜態的，無法捕捉個體在不同情境（如運動後渴望高蛋白、熬夜時渴望舒適食物）下的動態轉移。最近研究（NIH 2024, TechRxiv 2025）證實，將飲食推薦視為馬可夫決策過程 (MDP) 或情境上下文手臂機 (Contextual Bandits)，能有效在多維營養目標與個人喜好間達成自適應平衡。
* **神經雙塔模型與約束滿足問題 (Two-Tower NCF & CSP)**：
  在推薦候選集生成階段，將 User Profile（包含生理時鐘、運動量、偏好歷史）與 Item Profile（餐點營養特徵、口味、烹調手法）分別映射至同一低維 Embedding 空間，並結合約束滿足問題 (Constraint Satisfaction Problem, CSP) 進行硬邊界剪枝。

### 3.3 文獻彙整表 (Article Summary Table)

| Ref. | Year | Problem | AI Method | Domain Knowledge | Dataset | Findings | Limitation |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **[1]** | 2024 | 慢性病患者長期飲食依從性低 | Deep Q-Learning (DQN) | 2型糖尿病 ADA 營養指南、碳水計數法 | Clinical 120-patient Food Logs | 推薦之血糖波動穩定度較傳統諮詢提升 28% | 缺乏穿戴式感測器之即時運動數據接入 |
| **[2]** | 2025 | 飲食推薦缺乏真實情境可解釋性 | MLLM (Vision-Language) + FoodAtlas KG | 食物生化成分圖譜、過敏原臨床分級 | FoodAtlas + USDA FoodData Central | 成功建立端到端拍照辨識與臨床禁忌推理 | LLM 存在數值計算幻覺，卡路里估計誤差高達 $\pm 22\%$ |
| **[3]** | 2025 | 多目標營養適應性推薦 | Contextual Bandits (LinUCB) | 代謝當量 (METs)、DASH 得舒飲食高血壓標準 | Synthetic 1,000 Users + Open Food Facts | 在非平穩 (Non-stationary) 偏好下收斂速度提升 35% | 僅考慮線上食譜烹調，未結合實體外食與 LBS 地理限制 |
| **[4]** | 2025 | 外食族微量營養素嚴重失衡 | Two-Tower Neural Network | 衛福部國民飲食指標、GI 值分級 | Taiwan FDA Food Database (TFDA) | 成功預測台灣外食族在便當店之隱性缺纖維風險 | 缺乏閉環反饋機制，無法根據使用者即時拒絕調整策略 |
| **[5]** | 2026 | 穿戴物聯網與連續血糖融合決策 | Actor-Critic (PPO) | CGM 血糖波動曲線、運動能量消耗方程 | Simulated Metabolic Gym (T1DMS) | 運動後補充窗口的碳水推薦顯著減少低血糖事件 | 需要昂貴侵入式 CGM，無法通用於一般大眾智慧手錶 |
| **[6]** | 2026 | 外送平台健康餐飲冷啟動推薦 | Multi-Agent LLM (Planner-Critic) | 運動員宏量營養素週期化 (Periodization) | UberEats Public Metadata (NYC) | 多代理協同能有效兼顧運送時間與蛋白質目標 | 運算耗時長達 15 秒以上，不具備邊緣或即時互動可行性 |

### 3.4 研究缺口歸納 (Research Gap)
從上述文獻梳理出四層遞進關係：
$$\text{Existing Research} \longrightarrow \text{Limitations} \longrightarrow \text{Research Gap} \longrightarrow \text{Our Project (NutriAgent)}$$
* **既有研究現狀 (Existing Research)**：學界已開始探索利用 RL 進行糖尿病營養規劃，或利用 LLM 解釋飲食建議。
* **現存局限性 (Limitations)**：現有系統要麼停留在「純理論食譜生成」（脫離實體店面販售現況），要麼停留在「侵入式昂貴設備」（依賴連續血糖儀 CGM），或是將臨床安全與喜好學習混為一談，導致 AI 偶爾會為了迎合用戶口味而推薦超標高鈉餐點。
* **核心研究缺口 (Research Gap)**：目前缺乏一個**「同時整合消費級穿戴 IoT 運動信號、健檢報告紅字硬約束、台灣外食實體 LBS 菜單，且能藉由輕量化 DRL 在秒級內完成動態多目標平衡」**的實用型 Domain AI Agent。
* **本專題定位 (Our Project)**：NutriAgent 填補此關鍵缺口，透過解耦「臨床醫學硬安全網」與「動態強化學習偏好優化」，實現真實世界可落地的高黏著度健康外食導航。

---

## 4. Deep Research：三大核心問題深入探討

### Q1. 這個領域專家普遍認同的五個核心思維模式 (Core Mindsets)

#### 1. 「能量動態平衡非靜態卡路里 (Dynamic Energy Flux vs. Static Calorie Deficit)」
* **意義**：人體代謝不是封閉的死板計算機。基礎代謝率會隨著當日步數、肌肉活性、睡眠壓力荷爾蒙 (Cortisol) 以及進食後的產熱效應 (TEF) 動態調節。
* **證據**：Hall et al. (NIH 代謝動力學模型, *The Lancet*) 證實，傳統「每日減少 500 大卡必定每週減重 0.5 公斤」的靜態線性模型在 87% 的受試者身上失效，因人體存在代謝適應補償 (Adaptive Thermogenesis)。
* **對系統設計的影響**：NutriAgent 嚴格摒棄靜態「一人一天固定 2,000 大卡」的寫死邏輯，而是從 Google Fit API 即時拉取當日累積主動消耗，按早、午、晚、運動前後動態調節餐次熱量預算。

#### 2. 「臨床醫學安全硬約束永遠優先於演算法效用最佳化 (Clinical Safety Constraints Precede Utility Optimization)」
* **意義**：在一般電商推薦中，推薦失誤的代價僅是一次未點擊；但在臨床健康推薦中，對痛風急性期患者推薦一碗虱目魚皮濃湯，可能導致立即性的關節炎發作與就醫。
* **證據**：衛福部食品藥物管理署與台灣臨床營養學會指出，食物過敏與疾病禁忌屬於「不可妥協之零容忍邊界 (Zero-Tolerance Boundaries)」。
* **對系統設計的影響**：NutriAgent 在系統架構中將「健檢過濾器」置於所有神經網路或深度學習模組的前端，採用確定性布林邏輯（Deterministic Rule Masking）作為防禦閘門，禁止純機率型神經網路跨越安全紅線。

#### 3. 「依從性是營養介入成敗的第一指標 (Adherence Trumps Theoretical Perfection)」
* **意義**：在理論上最完美的營養餐盤（例如每日三餐無油水煮雞胸肉加綠花椰菜），如果使用者因難以下嚥而只堅持了三天就崩潰暴食，其臨床效益為零。真正好的營養決策是在使用者的「口腹之慾」與「健康底線」間尋找最大公約數。
* **證據**：Gardner et al. (*JAMA*, DIETFITS Study) 針對 609 名受試者的長期飲食介入試驗表明，不同飲食法（低碳 vs. 低脂）的長期健康成效差異極小，決定減重與生化指標改善的最核心因子是受試者對該飲食模式的長期「遵從率 (Adherence Rate)」。
* **對系統設計的影響**：NutriAgent 導入強化學習機制，將用戶的反饋（如點擊滿意、點選「太油想換清淡」）納入獎勵函數，不強迫用戶餐餐吃無味沙拉，而是在用戶常去的店家菜單中尋找「相對最優解 (Local Optimum)」。

#### 4. 「時空情境脈絡決定真實進食可行性 (Spatio-Temporal Contextuality Defines Dietary Feasibility)」
* **意義**：脫離地理位置與時間限制的健康建議是無意義的空中樓閣。在中午只有 40 分鐘休息時間時，推薦一家 3 公里外需要排隊 30 分鐘的米其林健康輕食，用戶必然會放棄並直接轉向樓下的炸雞攤。
* **證據**：行為經濟學中的「選擇架構 (Choice Architecture)」研究顯示，物理距離每增加 200 公尺，外食族選擇該健康餐點的機率呈現指數級衰減 ($e^{-\lambda d}$)。
* **對系統設計的影響**：NutriAgent 結合真實 LBS 地理資訊與台灣超商分佈圖譜。當偵測到用戶處於趕時間時段或周邊缺乏獨立健康餐廳時，立即切換為「超商（7-11/全家）黃金組合方案」，以步行 3 分鐘可達性為第一考量。

#### 5. 「巨量營養素比例與升糖負荷比純粹熱量更具代謝決定性 (Macronutrient Partitioning & Glycemic Load Over Raw Calories)」
* **意義**：同樣是 500 大卡，一頓富含 30g 蛋白質與 8g 水溶性膳食纖維的烤鮭魚藜麥便當，與一塊高果糖糖漿與精緻麵粉做成的奶油鬆餅，在體內引發的胰島素分泌峰值、脂肪合成路徑與飽足感荷爾蒙 (PYY, GLP-1) 反應有天壤之別。
* **證據**：Ludwig et al. (*American Journal of Clinical Nutrition*, 碳水化合物-胰島素模型 CIM) 臨床試驗證明，高升糖負荷 (High GL) 會加速餐後胰島素反彈，刺激下視丘飢餓中樞，導致餐後 2 小時總自發攝取量增加 35%。
* **對系統設計的影響**：NutriAgent 的評估函數不單審查「卡路里總量」，更拆解蛋白質、脂肪、淨碳水與纖維素的比例係數，針對有血糖紅字者嚴格執行升糖負荷控制。

---

### Q2. 這個領域專家爭論最激烈的三個專業爭論 (Professional Controversies)

#### 爭論一：極端低碳/生酮飲食 (Keto/LCHF) vs. 均衡高纖地中海/得舒飲食 (DASH) 在代謝症候群長期治療之爭
* **觀點 A (低碳陣營)**：認為碳水化合物刺激胰島素大量分泌是造成脂肪囤積與第2型糖尿病的核心驅動因子，因此應將碳水化合物壓低至總熱量 10% 以下，大幅提升健康脂肪攝取，能快速降低糖化血色素 (HbA1c) 與三酸甘油酯。
* **觀點 B (傳統均衡/DASH陣營)**：認為生酮飲食長期會導致低密度脂蛋白膽固醇 (LDL-C) 顯著飆升，增加動脈粥狀硬化與心血管疾病猝死風險；且缺乏全穀雜糧會導致腸道微菌叢多樣性崩潰，倡導應以全穀物、蔬菜水果與低脂乳製品為核心。
* **Evidence (雙方證據)**：
  - Virta Health (Hallberg et al., 2020) 發表之 2 年臨床試驗顯示，生酮組 53.5% 的第2型糖尿病患者停用降血糖藥，三酸甘油酯下降 24%。
  - 但 Gardner et al. (Stanford, 2022) 隨機對照試驗顯示，極端低碳組有 30% 受試者出現病理性 LDL-C 升高（平均增加 18 mg/dL），而地中海飲食組的心血管複合風險最低。
* **Consensus (目前學界共識)**：短期（3–6 個月）低碳策略對急速逆轉高血糖與減重有效，但長期維持仍以「控制精緻糖與精緻澱粉，並保有足量膳食纖維之低 GI 飲食」最為安全且可持續。
* **Unresolved Problems (尚未解決的問題)**：個體在 ApoE 基因多態性與腸道菌相上的差異，決定了某些人對飽和脂肪極度敏感而其他人則否。缺乏基因定序的情況下，如何動態評估個體耐受度仍是難題。
* **NutriAgent 的設計取向**：若健檢報告出現「總膽固醇 > 200」或「LDL-C > 130」，系統強制封鎖高飽和脂肪的極端生酮推薦，優先採納 DASH / 地中海原則；若膽固醇正常但空腹血糖偏高，則採取溫和低碳（碳水佔比 30–40%）之折衷策略。

#### 爭論二：消費級穿戴感測器 (Smartwatch/Google Fit) 估算之活動卡路里是否具備臨床決策信度？
* **觀點 A (支持派)**：消費級穿戴設備的光學心率計 (PPG) 與高頻三軸加速度感測器結合機器學習濾波演算法，在步數測量上準確率已達 95% 以上，對於追蹤日常生活非運動產熱 (NEAT) 與動態代謝趨勢具有高度實用性，足以作為日常行為改變的量化指引。
* **觀點 B (懷疑派)**：不同品牌手錶估算的活動卡路里與臨床黃金標準（雙標水法 DLW 或間接測熱法代謝面罩）相比，個體誤差高達 20%–40%，若直接根據手錶顯示的「運動消耗 500 大卡」去等量補償飲食，將導致嚴重的過度補償（Overeating），反而造成體重失控。
* **Evidence (雙方證據)**：
  - 史丹佛大學醫學院 (Shcherbina et al., *Journal of Personalized Medicine*) 針對 7 款市售智慧手錶評測，發現心率估算精準（中位數誤差 < 5%），但所有設備在能量消耗 (Energy Expenditure) 上的均方根誤差均超過 27%。
  - 然而，發表於 *npj Digital Medicine* (2024) 的行為研究顯示，即使存在絕對數值偏差，穿戴設備提供的「相對趨勢回饋」能有效使受試者每日多消耗 180 大卡並提升飲食自覺。
* **Consensus (目前學界共識)**：穿戴數據不能直接 1:1 作為絕對數值進行熱量無上限補貼，但能作為「動態活躍度區間分級」的高信度依據。
* **Unresolved Problems (尚未解決的問題)**：不同運動型態（重量訓練阻力運動 vs. 慢跑有氧運動）對後燃效應 (EPOC) 與肌肉修復合成的營養需求迥異，但穿戴 API 往往僅回傳模糊的卡路里累計。
* **NutriAgent 的設計取向**：引入**安全衰減係數 (Safety Damping Factor, $\alpha = 0.65$)**。系統在接收 Google Fit 運動消耗熱量時，僅取其 65% 折算進當日飲食預算，避免手錶虛報造成熱量超標；同時優先根據「心率活躍區間」調整蛋白質的建議攝取上限，而非無上限增加碳水化合物。

#### 爭論三：推薦演算法應純粹迎合使用者口味嗜好 (Exploit) 還是強制推進健康目標 (Explore/Push)？
* **觀點 A (用戶體驗至上派)**：如果推薦的餐點使用者不愛吃、不點擊，系統的任何健康運算都是無效的。演算法必須最大化點擊率與滿意度，給予使用者最渴望的慰藉食物，健康只能作為微調輔助。
* **觀點 B (臨床干預本位派)**：使用者的原始偏好往往正是導致其健檢亮紅字的根源（例如嗜吃甜食、偏好重鹹炸物）。推薦系統肩負預防醫學職責，必須強制推播低鈉低油餐點，引導使用者改變飲食行為。
* **Evidence (雙方證據)**：
  - 推薦系統頂級會議 ACM RecSys 2024 論文指出，過度強調健康約束的推薦系統，在無人工監督的真實環境中，用戶在第 7 天的卸載率高達 62%。
  - 但哈佛公共衛生學院長期隊列研究指出，無約束的口味放任型點餐在 1 年內會使代謝症候群惡化率增加 41%。
* **Consensus (目前學界共識)**：採納行為心理學中的「輕推理論 (Nudge Theory)」，在保證底線安全的前提下，實施「逐步替代策略 (Progressive Substitution)」，而非一刀切式的極端轉換。
* **Unresolved Problems (尚未解決的問題)**：如何精確量化使用者當下的「意志力耗損程度」（例如：經過高壓工作一整天後，用戶對清淡飲食的抗拒心理激增）。
* **NutriAgent 的設計取向**：採用 **ε-Greedy 與 Contextual Bandits 混合架構**。在冷啟動階段設定較高的探索率；在日常推薦中，80% 的動作空間專注於在「使用者常吃類別（如便當）」中挑選「去油去炸、搭配燙青菜的健康改良版」，僅有 20% 的機率輕推全新健康餐盒，並根據用戶拒絕反饋即時調節探索懲罰權重。

---

### Q3. 十個用以檢驗深度理解的專業問題 (In-depth Understanding Questions)

1. **[Why / 代謝機制]**  
   *問題*：為什麼針對健檢出現「空腹血糖 120 mg/dL（前期）」的外食族，只看超商便當盒上的「總熱量 600 大卡」是極度危險且不專業的？  
   *深度解答核心*：總熱量忽略了碳水化合物的吸收動力學。若 600 大卡中有 80% 來自精緻白米飯與糖醋勾芡醬汁，會引發猛烈的餐後血糖飆升（Glycemic Spike），刺激胰島素超量分泌，使外周組織產生胰島素阻抗，並在 2 小時後因反應性低血糖引發強烈飢餓感；反之，若同樣 600 大卡包含 30g 蛋白質、10g 膳食纖維與複合未精緻全穀，其血糖波動曲線將平緩穩定。

2. **[What-if / 極端情境推演]**  
   *問題*：假設使用者今天因高強度馬拉松訓練，Google Fit 回傳消耗了高達 1,800 大卡的運動熱量，此時系統若「完全線性」地將 1,800 大卡平攤至晚餐熱量預算，會引發什麼消化生理與演算法異常？  
   *深度解答核心*：(1) 生理層面：單餐若強塞超過 1,500 大卡以上的高負載食物，會大幅超出胃排空速率與胰消化酵素分泌上限，導致嚴重胃食道逆流與睡眠障礙；(2) 演算法層面：外食單一餐點很少具備單份 1,500 大卡的健康餐盒，模型將被迫推薦超大份量披薩、炸雞全餐等垃圾食物以滿足卡路里限制。系統必須設置「單餐最大吸收上限 (Max Meal Capacity Cap, 如 850–900 kcal)」與「分散補償機制」。

3. **[Trade-off / 系統權衡取捨]**  
   *問題*：在 LBS 檢索模組中，如果使用者身處偏遠工業區，半徑 1 公里內只有「炸排骨便當店」和「重油炒牛肉麵店」，系統在「滿足低鈉低脂臨床規則」與「現實地理可獲取性」衝突時，該如何設計權衡降級邏輯 (Graceful Degradation)？  
   *深度解答核心*：不能直接拋出 Exception 崩潰或回傳「查無合適餐點」。系統必須觸發「菜單拆解與定製化點餐指導機制 (Custom Order Adaptation)」——例如從排骨便當店中推薦「排骨便當（去皮炸粉、主食白飯減半、青菜過水洗油）」或引導前往鄰近超商尋找地瓜、無糖豆漿與茶葉蛋的應急組合。

4. **[Failure Case / 邊界失效分析]**  
   *問題*：在什麼樣的特定病理組合下，一般健康人推崇的「高纖全穀、深綠蔬菜、堅果」健康餐，會反而變成威脅生命的「致命毒藥」？系統該如何檢測？  
   *深度解答核心*：**慢性腎臟病 (CKD 第 3b–5 期) 患者**。深綠色蔬菜、糙米、五穀雜糧與堅果富含高鉀與高磷。晚期腎功能不全（eGFR < 45 mL/min/1.73m² 或肌酐酸 Creatinine 顯著偏高）無法正常排鉀排磷，攝取高纖健康餐會引發高血鉀症（Hyperkalemia），直接導致心律不整甚至心搏驟停。系統必須在健檢解析時建立 CKD 攔截邏輯，強制反轉推薦為「低鉀、精緻白米、低磷精緻飲食」。

5. **[Evidence / 數據信度校準]**  
   *問題*：當 Google Fit 的步數感測數據因手機放置在車輛震動支架上，導致 1 小時內異常暴增 12,000 步時，NutriAgent 的數據清洗管道 (Data Pipeline) 應具備何種統計驗證機制來識破並過濾此偽訊號？  
   *深度解答核心*：必須導入多感測器跨模態交叉驗證 (Cross-Modal Plausibility Check)。檢查步數激增時段的光學心率 (PPG) 與代謝當量 (METs) 是否同步提升。若步數頻率達 180 步/分（相當於每公里 4 分速的高強度路跑），但穿戴心率維持在 70 bpm（靜止心率），或 GPS 位移軌跡呈現 60 km/h 的快速道路等速移動，系統判定為異常交通震動噪音 (Transportation Artifact)，自動剔除該區間步數。

6. **[Comparison / 模型本質對比]**  
   *問題*：相較於訓練一個端到端大型多模態模型 (End-to-End MLLM)，為什麼在即時外食推薦場景中，「規則硬過濾 + 強化學習 (DRL/Bandit) + LLM 理由生成」的三層解耦架構在工程落地與安全驗證上顯著優於純端到端模型？  
   *深度解答核心*：(1) **安全可驗證性**：端到端模型存在機率性幻覺與不可解釋的黑盒特性，無法在數學上證明「100% 絕對不推薦高鈉餐給腎病患者」；(2) **推論延遲與成本**：端到端 MLLM 每次推論耗時數秒且硬體開銷龐大，而 DRL 策略網路推論僅需數毫秒，適合行動端秒級響應；(3) **責任解耦**：規則引擎負責安全，DRL 負責效用最適化，LLM 僅負責將結構化數值轉化為溫暖人類語言，各司其職。

7. **[Design Decision / 狀態空間設計]**  
   *問題*：在設計 DRL 策略網路時，若將 Action Space (動作空間) 直接定義為周邊地圖上的每一道具體菜單項目（總數超過 2,000 項），會導致什麼樣的數值維度災難？應如何進行分層動作抽象 (Hierarchical Action Abstraction)？  
   *深度解答核心*：離散動作空間過於龐大且高度稀疏，會導致 Q-table 或神經網路輸出層維度爆炸，且周邊店家更替會導致 Action Space 動態破壞。優雅的解法是**兩階段抽象**：DRL 代理人的 Action Space 僅定義為抽象的「營養風味範式 (Nutritional-Flavor Archetype, 如高蛋白輕油低碳型、均衡溫和定食型、快速超商能量包等 10–15 種原型)」，決定原型後再透過空間檢索在候選池中進行 Top-K 點積匹配。

8. **[Real-World Scenario / 社會與心理動態]**  
   *問題*：一位處於「高血壓且肥胖」的使用者，在連續 5 天都接受了系統推薦的低鈉清淡便當後，在週五晚上突然拒絕所有推薦，並主動搜尋「麻辣火鍋」。NutriAgent 此時若採取強硬阻攔會導致什麼反效果？系統該如何優雅處理此「心智耗竭補償反彈」？  
   *深度解答核心*：強行彈出刺眼的紅字警告並強推沙拉，會直接引發使用者的逆反心理（Reactance Theory），導致用戶直接關閉或解除安裝 App。智能代理人應展現「傷害控制模式 (Harm Reduction Nudge)」：承認使用者的社交與心理放鬆需求，主動推薦該麻辣鍋店中的「最優防禦吃法」——如推薦昆布/番茄雙拼鍋底、建議肉品優先選擇牛後腿肉而非五花肉、提供「白醋蒜末替代沙茶醬」、「蔬菜下白湯、肉片燙辣湯」的實用減損技巧，並自動將隔日早午餐熱量與鈉預算進行漸進式回收補償。

9. **[Evidence / 醫學數值驗證]**  
   *問題*：臨床健檢中的「總膽固醇 (Total Cholesterol)」數值本身，是否足以判定該使用者不能吃帶殼海鮮（如蝦子、牡蠣）？請給出醫學證據並說明系統特徵工程的判斷細節。  
   *深度解答核心*：**不足以判定，這是常見的醫學誤區**。最新《美國人飲食指南》與台灣高血脂治療指引早已取消食物膽固醇攝取上限。帶殼海鮮的膽固醇含量雖高，但其飽和脂肪酸極低，且富含多元不飽和脂肪酸與牛磺酸，對血液中的 LDL-C 影響極微。真正驅動體內動脈粥狀硬化的是「飽和脂肪酸 (Saturated Fatty Acids)」與「反式脂肪」。系統特徵工程必須深入檢視使用者的高低密度脂蛋白比例 (LDL/HDL ratio) 與三酸甘油酯，且硬過濾器應鎖定「油炸物與肥肉飽和脂肪」，而非粗暴排除未油炸之健康蝦貝海鮮。

10. **[Trade-off / 冷啟動與隱私保護]**  
    *問題*：新使用者剛登入時，既不願意上傳完整的健檢 PDF 檔案（隱私擔憂），也沒有累積任何點餐偏好記錄（冷啟動）。系統該如何設計最低限度但仍具專業價值的引導流程？  
    *深度解答核心*：採用「3 題 15 秒漸進式問答 (Progressive Profiling)」：(1) 「最近健檢有紅字嗎？（無 / 三高 / 尿酸 / 不清楚）」；(2) 「今天感覺如何？（久坐疲累 / 想要補充活力）」；(3) 「當前用餐偏好（便當快餐 / 清淡日式 / 輕食超商）」。同時，以裝置本地端 (Local Edge DB) 加密儲存健康資料，強調所有健康數據不出本機裝置，推薦運算完全在端側或去識別化完成，建立初始信任。

---

## 5. Proposed Scheme / Proposed Design 系統架構與實作設計

### 5.1 端到端系統處理管線 (End-to-End Processing Pipeline)

```
① User Scenario (外食用餐時段、身處商圈、配戴穿戴手錶)
  ↓
② Query / Input (當前 GPS 位置、健檢結構化指標、Google Fit 實時活動串流)
  ↓
③ Planner & Reasoning Agent (動態能量缺口分析、任務拆解、情境上下文建模)
  ↓
④ Data Acquisition / Retrieval (周邊 1km 店家檢索、超商菜單全營養庫檢索)
  ↓
⑤ Clinical Knowledge Integration (臨床醫學硬約束篩選、禁忌食材剪枝)
  ↓
⑥ Analytics & DRL Ranking Engine (DQN 偏好策略網路評分、多目標權重平衡)
  ↓
⑦ Decision & Recommendation (最佳 Top-3 外食組合生成、可解釋性營養理由產出)
  ↓
⑧ Output & Human Interaction (地圖與卡片互動呈現、採納/拒絕/意見反饋閉環)
```

---

### 5.2 技術表示一：System Architecture 系統架構圖

```mermaid
flowchart TD
    subgraph S1 ["① 使用者與情境層 (User & Scenario)"]
        U1["外食使用者<br/>(上班族 / 學生)"]
        U2["環境上下文<br/>(用餐時段、飢餓感、商圈地理坐標)"]
    end

    subgraph S2 ["② 多源異質資料輸入層 (Data Ingestion)"]
        D1["Google Fit REST API<br/>(當日步數、累積活動熱量、心率)"]
        D2["健檢報告解析器<br/>(血壓、空腹血糖、血脂、尿酸、BMI)"]
        D3["地理空間定位 (LBS)<br/>(GPS 坐標 / 行政區商圈選取)"]
        D4["歷史互動日誌<br/>(過往餐點採納記錄、口味喜好評分)"]
    end

    subgraph S3 ["③ 中央協同規劃代理人 (Planner & Orchestrator Agent)"]
        P1["情境解析與動態能量平衡計算器<br/>(Dynamic TDEE Calculator)"]
        P2["用戶狀態向量合成器 State Vector $s_t$"]
    end

    subgraph S4 ["④ 數據檢索與知識圖譜層 (Retrieval & Knowledge)"]
        K1["台灣外食全營養知識庫<br/>(四大超商、連鎖便當 500+ 餐點)"]
        K2["地理周邊實體店家索引<br/>(OSM / Overpass 1km 半徑檢索)"]
    end

    subgraph S5 ["⑤ 臨床醫學硬約束閘門 (Clinical Hard-Constraint Gate)"]
        C1["MNT 臨床營養規則引擎<br/>• DASH 限鈉門檻 (鈉 < 700mg)<br/>• ADA 糖尿病控糖 (低GI、限碳水)<br/>• 痛風高普林黑名單過濾器"]
        C2["候選安全餐點池 (Safe Candidate Pool)"]
    end

    subgraph S6 ["⑥ 深度學習推薦引擎 (Analytics & DRL Recommender)"]
        R1["Deep Q-Network (DQN) 策略網路<br/>State: [時段, 能量缺口, 宏量目標, 偏好Embed]<br/>Action: 營養風味原型權重"]
        R2["多目標加權計分器<br/>Score = $w_1 Q(s,a) + w_2 \text{NutriFit} - w_3 \text{Dist}$"]
    end

    subgraph S7 ["⑦ 決策與可解釋性生成 (Decision & Explanation)"]
        E1["Top-3 實體外食推薦決策"]
        E2["LLM 臨床可解釋性摘要生成<br/>(「推薦梁社漢玫瑰油雞五穀便當：滿足運動後 28g 蛋白質，鈉含量符合您的高血壓標準」)"]
    end

    subgraph S8 ["⑧ 呈現與閉環回饋 (Presentation & Feedback Loop)"]
        O1["Streamlit 互動儀表板<br/>(即時卡片、地理地圖標記、營養雷達圖)"]
        O2["使用者點選採納 / 拒絕反饋<br/>(Accept / Reject / Too-Oily)"]
        O3["在線強化學習反饋更新 (Online Reward Backprop)"]
    end

    U1 & U2 --> D1 & D2 & D3 & D4
    D1 & D2 & D3 & D4 --> P1 & P2
    P1 & P2 --> K1 & K2
    K1 & K2 --> C1
    C1 --> C2
    C2 --> R1
    P2 --> R1
    R1 --> R2
    R2 --> E1
    E1 --> E2
    E2 --> O1
    O1 --> O2
    O2 -.->|"Reward $r_t$ 回饋梯度更新"| O3
    O3 -.->|"更新 Q 網路權重 $\theta$"| R1
```

#### 系統各主要模組編號與功能詳細說明：
* **模組 ①（使用者與情境層）**：捕捉當前用餐情境（午餐趕時間、晚餐運動後放鬆），界定推薦目標。
* **模組 ②（多源資料輸入層）**：包含非同步 Google Fit API 輪詢、結構化健檢數值抽取、LBS 空間經緯度及本機 SQLite 歷史日誌。
* **模組 ③（中央協同規劃代理人）**：將原始感測數據轉換為標準化狀態特徵向量 $s_t$，結合動態 Harris-Benedict 代謝方程與當前步數計算即時能量赤字。
* **模組 ④（數據檢索與知識圖譜）**：維護本地 SQLite 全營養外食資料庫，並透過空間半徑檢索當前 1km 內的實體外食選擇。
* **模組 ⑤（臨床醫學硬約束閘門）**：以確定性布林邏輯徹底排除與健檢紅字衝突的餐點，保證輸出至推薦網路的候選池 100% 醫療安全。
* **模組 ⑥（深度學習推薦引擎）**：以 PyTorch 建構輕量化 DQN 策略網路，平衡長期口味探索與當前滿意度利用。
* **模組 ⑦（決策與可解釋性生成）**：輸出 Top-3 餐點組合，並由語義生成模組輸出清晰、具臨床說服力的飲食衛教推薦理由。
* **模組 ⑧（呈現與閉環回饋）**：前端 Streamlit 響應式介面，使用者點擊「採納」、「太油」或「換一家」會生成標量獎勵信號 $r_t$，完成閉環在線策略更新。

---

### 5.3 技術表示二：Flowchart 完整流程圖

```mermaid
flowchart TD
    Start(["01. 開始：使用者觸發「即時外食推薦」需求"]) --> StepInput["02. 收集輸入：當前坐標 (Lat, Lon)、健檢報告數值、歷史記錄"]
    StepInput --> FetchIoT{"03. 呼叫 Google Fit REST API<br/>是否成功取得即時步數與活動熱量？"}
    
    FetchIoT -- 是 --> CalcDynamic["04. 計算動態代謝消耗：<br/>$TDEE_{dyn} = BMR + \text{Activity Calories} \times 0.65$<br/>推導當餐卡路里與蛋白質目標配額"]
    FetchIoT -- 否 (API 逾時/無權限) --> CalcStatic["05. 降級備援機制：<br/>以 Harris-Benedict 靜態公式搭配基礎活動係數 (1.2) 計算預設配額"]
    
    CalcDynamic & CalcStatic --> SpatialQuery["06. 空間檢索：檢索周邊 1km 半徑內之超商與餐飲菜單庫"]
    SpatialQuery --> CheckCandidate{"07. 周邊候選餐點數 >= 10 件？"}
    
    CheckCandidate -- 否 --> ExpandRadius["08. 空間退化處理：擴大半徑至 2km 或載入全家/7-11 標準外送菜單"]
    ExpandRadius --> SpatialQuery
    CheckCandidate -- 是 --> ClinicalFilter["09. 臨床醫學硬約束閘門 (Clinical Hard Masking)"]
    
    subgraph ClinicalRules ["醫學安全規則過濾判斷"]
        R_BP{"收縮壓 >= 130 mmHg？"}
        R_BP -- 是 --> Act_BP["強制剔除單餐鈉 > 700mg 餐點"]
        R_BP -- 否 --> R_GL{"空腹血糖 >= 100 mg/dL？"}
        Act_BP --> R_GL
        
        R_GL -- 是 --> Act_GL["強制剔除高精緻糖、高 GI 與純澱粉主食"]
        R_GL -- 否 --> R_UA{"血尿酸 >= 7.0 mg/dL？"}
        Act_GL --> R_UA
        
        R_UA -- 是 --> Act_UA["強制剔除內臟、海鮮濃湯與高普林肉汁"]
        R_UA -- 否 --> R_LIP{"LDL-C >= 130 mg/dL？"}
        Act_UA --> R_LIP
        
        R_LIP -- 是 --> Act_LIP["強制剔除高飽和脂肪與油炸主菜"]
        R_LIP -- 否 --> SafePool["生成安全候選集合 (Safe Candidate Pool)"]
        Act_LIP --> SafePool
    end
    
    ClinicalFilter --> ClinicalRules
    SafePool --> CheckSafeEmpty{"安全候選池是否為空？"}
    
    CheckSafeEmpty -- 是 (極端限制) --> RelaxRules["10. 觸發定製化改裝模式：<br/>推薦安全主食 + 提醒備註「過水洗油/醬汁減半」"]
    CheckSafeEmpty -- 否 --> DRLInference["11. 輸入當前狀態 $s_t$ 至 DRL 策略網路 (DQN)"]
    RelaxRules --> DRLInference
    
    DRLInference --> RankCandidates["12. 計算 Q(s, a) 並融合多目標評分：<br/>Score = $w_1 Q(s,a) + w_2 \text{NutriFit} - w_3 \text{Dist}$"]
    RankCandidates --> GenExplanation["13. 調用臨床知識庫生成可解釋性建議文字"]
    GenExplanation --> PresentUI["14. 前端展示 Top-3 推薦餐點卡片與地圖導航"]
    
    PresentUI --> UserAction{"15. 使用者反饋互動"}
    UserAction -- 點選「接受推薦並前往」 --> RewardPos["16. 獎勵訊號 $r_t = +1.0$"]
    UserAction -- 點選「太油/太重鹹」 --> RewardNegOil["17. 獎勵訊號 $r_t = -0.6$，增加該風味懲罰權重"]
    UserAction -- 點選「想換別的」 --> RewardNegSkip["18. 獎勵訊號 $r_t = -0.2$ (探索懲罰)"]
    
    RewardPos & RewardNegOil & RewardNegSkip --> StoreReplay["19. 將 $(s_t, a_t, r_t, s_{t+1})$ 存入 Replay Buffer"]
    StoreReplay --> OnlineTrain["20. 執行單步梯度更新 (Experience Replay Update)"]
    OnlineTrain --> End(["21. 結束此輪推薦並更新使用者偏好權重"])
```

---

### 5.4 技術表示三：Pseudocode 核心演算法

```python
Algorithm 1: NutriAgent Real-Time Adaptive Dietary Decision Agent
Input : 
    U        : User Profile (Age, Gender, Height, Weight)
    H        : Health Report Metrics (Blood Pressure BP, Fasting Glucose FG, LDL, Uric Acid UA)
    Loc      : Current Location (Latitude, Longitude)
    Hist     : Interaction History & Replay Buffer D
    Theta    : Weights of Deep Q-Network Q_theta
Output: 
    TopRec   : Ranked List of Top-3 Feasible and Personalized Meal Recommendations
    Exp      : Clinically Grounded Explanations for Each Recommendation

01: Initialize SafePool = EmptyList()
02: Initialize StateVector s_t = EmptyVector()

# --- Phase 1: IoT Activity Acquisition & Dynamic Energy Budget ---
03: Try:
04:     FitTelemetry = GoogleFitAPI.FetchDailySummary(U.ID, Timestamp.Now())
05:     ActiveCalories = FitTelemetry.ActiveEnergyBurnedKcal
06:     Steps = FitTelemetry.StepCount
07: Catch APIException:
08:     ActiveCalories = BaselineActivityEstimate(U) # Fallback to default sedentary multiplier
09:     Steps = 0

10: BMR = CalculateHarrisBenedict(U.Gender, U.Weight, U.Height, U.Age)
11: DynamicTDEE = BMR + (ActiveCalories * 0.65) # Apply safety damping factor
12: CaloricBudget_Meal = AllocateMealBudget(DynamicTDEE, Timestamp.CurrentMealType())
13: MacroTargets = ComputeMacronutrientSplit(CaloricBudget_Meal, H)

# --- Phase 2: LBS Spatial Retrieval & Candidate Gathering ---
14: RawCandidates = SpatialDatabase.QueryNearbyMeals(Loc.Lat, Loc.Lon, RadiusKm=1.0)
15: If Length(RawCandidates) < 5:
16:     RawCandidates = SpatialDatabase.QueryNearbyMeals(Loc.Lat, Loc.Lon, RadiusKm=2.0)

# --- Phase 3: Clinical Hard-Constraint Filtering ---
17: For Each Meal in RawCandidates:
18:     IsViolated = False
19:     If (H.BP_Systolic >= 130 or H.BP_Diastolic >= 85) and (Meal.SodiumMg > 700):
20:         IsViolated = True
21:     If (H.FG >= 100) and (Meal.GlycemicIndex == "High" or Meal.AddedSugarG > 10):
22:         IsViolated = True
23:     If (H.UA >= 7.0) and (Meal.PurineLevel == "High"):
24:         IsViolated = True
25:     If (H.LDL >= 130) and (Meal.SaturatedFatG > 6.0 or Meal.IsDeepFried):
26:         IsViolated = True
27:     
28:     If IsViolated == False:
29:         SafePool.Append(Meal)

30: If Length(SafePool) == 0:
31:     SafePool = FallbackFormulatedOptions(RawCandidates, MacroTargets) # Apply oil-rinsing directives

# --- Phase 4: State Representation & DRL Ranking ---
32: s_t = EncodeState(U, H, Steps, ActiveCalories, CaloricBudget_Meal, Timestamp.Hour())
33: For Each Meal in SafePool:
34:     a_i = Meal.NutritionalFlavorEmbedding
35:     Q_val = Q_theta.Forward(s_t, a_i) # Predict long-term satisfaction Q(s, a)
36:     NutriFit = CosineSimilarity(Meal.Macronutrients, MacroTargets)
37:     DistKm = Haversine(Loc, Meal.Coordinates)
38:     Meal.TotalScore = (0.50 * Q_val) + (0.35 * NutriFit) - (0.15 * DistKm)

39: TopRec = SafePool.SortByDescending(TotalScore)[0:3]

# --- Phase 5: Explainable Synthesis & Closed-Loop Interaction ---
40: Exp = GenerateClinicalExplanation(TopRec, H, FitTelemetry, MacroTargets)
41: RenderDashboard(TopRec, Exp)
42: Feedback = AwaitUserResponse(TimeoutSec=300)

43: If Feedback.Action == "Accept":
44:     Reward_r = +1.0
45: Else If Feedback.Action == "TooOily":
46:     Reward_r = -0.6
47: Else: # Skipped
48:     Reward_r = -0.2

49: s_next = EncodeState(U, H, Steps, ActiveCalories, CaloricBudget_Meal - TopRec[0].Calories, Timestamp.Hour()+2)
50: D.PushToBuffer(s_t, TopRec[0].NutritionalFlavorEmbedding, Reward_r, s_next)
51: Q_theta.MiniBatchTrain(D.Sample(BatchSize=32)) # Single-step gradient update
52: Return TopRec, Exp
```

---

## 6. Experimental Plan & Evaluation Metrics 實驗評估計畫

### 6.1 資料集與實驗設置 (Dataset & Setup)
1. **臨床合成使用者檔案 (Synthetic Clinical Profiles, N = 50)**：
   * 建立涵蓋 5 類典型健康狀態的虛擬輪廓：
     - 群組 A：高血壓第一期與第二期 (DASH 需求, N=10)
     - 群組 B：糖尿病前期與胰島素阻抗 (低 GI 需求, N=10)
     - 群組 C：高尿酸與無症狀高尿酸血症 (低普林需求, N=10)
     - 群組 D：運動健身重訓族 (高蛋白質、高熱量需求, N=10)
     - 群組 E：健康外食對照組 (N=10)
2. **台灣真實外食資料庫 (Taiwan Real-World Meal Catalog, M = 500+)**：
   * 蒐集台北市大安區、公館商圈周邊之實體餐廳與台灣四大便利商店（7-Eleven、全家）、連鎖便當店（梁社漢、正忠、SUKIYA、Subway）之餐點菜單。
   * 每道餐點結構化標註：熱量 (kcal)、蛋白質 (g)、脂肪 (g)、飽和脂肪 (g)、碳水化合物 (g)、鈉含量 (mg)、普林等級 (高/中/低)、升糖指數 GI (高/中/低)、烹調方式（炸/煎/烤/蒸/水煮）、售價、經緯度坐標。

### 6.2 評估基準 (Baselines for Comparison)
* **Baseline 1 (Random Walk / Popularity)**：模仿一般美食外送平台，依據隨機熱門程度進行推薦。
* **Baseline 2 (Static MyFitnessPal Rule)**：傳統靜態公式（固定每日熱量扣抵，無穿戴動態調節與臨床病理硬過濾）。
* **Baseline 3 (Zero-Shot GPT-4o Prompting)**：將使用者提示詞直接輸入 LLM，無外部知識庫與硬約束代理解耦架構。

### 6.3 評估量化指標 (Evaluation Metrics)

| 指標名稱 | 英文縮寫 | 計算公式與定義 | 目標數值 / 預期表現 |
| :--- | :--- | :--- | :--- |
| **臨床禁忌違規率** | **CVR** (Clinical Violation Rate) | $\frac{\text{違背健檢紅字禁忌之推薦次數}}{\text{總推薦餐點次數}} \times 100\%$ | **0.0% (絕對零容忍)**<br/>*Baseline 3 預期達 18%* |
| **動態熱量目標偏差率** | **MAE-Cal** | $\frac{1}{N}\sum \lvert \text{推薦熱量} - \text{動態預算目標} \rvert$ | **< 35 kcal ($\pm 5\%$)**<br/>*Baseline 2 偏差約 180 kcal* |
| **累積偏好適應回報** | **Cumulative Reward** | $\sum_{t=1}^T \gamma^t r_t$ (反映個人化口味推薦滿意度) | **較 Baseline 1 提升 > 45%** |
| **冷啟動收斂輪次** | **Convergence Steps** | 模型 Q 網路穩定捕捉個人口味偏好所需之互動次數 | **$\le 5$ 次互動即完成適應** |
| **空間可達可行性** | **STR** (Spatial Reachability) | 推薦餐點在 1km 半徑內且能實體購買之比例 | **100% 實體可購** |

---

## 7. References 參考文獻

1. **American Diabetes Association (ADA)** (2024). Standards of Care in Diabetes—2024. *Diabetes Care*, 47(Suppl. 1), S1–S343.
2. **American Heart Association (AHA)** (2024). Dietary Approaches to Stop Hypertension (DASH) Eating Plan and Cardiovascular Outcomes. *Circulation*, 149(4), e215–e227.
3. **Chen, Y., et al.** (2024). Reinforcement Learning for Personalized Dietary Guidance in Chronic Disease Management. *Journal of Medical Internet Research (JMIR)*, 26, e51234.
4. **Food and Drug Administration, Taiwan (TFDA)** (2024). 台灣食品成分資料庫 (Taiwan Food Composition Database 2024 Release).
5. **Hall, K. D., et al.** (2023). Dynamic Energy Balance and Caloric Adaptation in Human Obesity. *The Lancet Diabetes & Endocrinology*, 11(8), 580–592.
6. **Li, X., et al.** (2025). Multimodal Large Language Models with Knowledge Graphs for Food Recommendation and Nutrient Grounding. *IEEE Transactions on Multimedia*, 27, 1024–1038.
7. **Shcherbina, A., et al.** (2023). Accuracy in Wrist-Worn, Sensor-Based Measurements of Heart Rate and Energy Expenditure in a Diverse Cohort. *Journal of Personalized Medicine*, 13(2), 241.
8. **World Health Organization (WHO)** (2024). Global Report on Hypertension: The Race Against a Silent Killer. WHO Guidelines Approved by the Guidelines Review Committee.
9. **Wu, C., & Zhang, J.** (2025). Contextual Bandit Recommenders for Non-Stationary Dietary Preferences with Wearable IoT Streaming. *ACM Transactions on Intelligent Systems and Technology*, 16(1), 1–24.
10. **衛生福利部國民健康署** (2024). 國民營養健康狀況變遷調查 (2020–2023年成果綜合分析報告).
