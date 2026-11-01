# NutriAgent 智動食健
## 結合物聯網感測與健檢知識圖譜之即時適應性外食營養決策代理人
### Real-Time Adaptive Dietary Decision Agent Integrating Wearable IoT Telemetry and Clinical Knowledge Graph

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-red.svg)](https://pytorch.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0%2B-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Proposal-100%25%20Complete-brightgreen.svg)]()

> **課程專題**：國立大學「物聯網應用與資料分析 (IoT Applications & Data Analysis)」期末專案  
> **核心架構**：`AI Agent + Domain Knowledge + Data Analytics + Real-World Application`  
> **交接標準**：*即使原開發者不在，下一位開發者仍能透過 GitHub + README.md + DESIGN.md 理解、執行、驗證並繼續開發此專題。*

---

## 📌 專案核心故事 (Abstract Story)

* **[Attention Getter — 動機]**：台灣成人代謝症候群盛行率高達 **34.6%**，超過 **72.8%** 的上班族與學生依賴外食。高鈉、高精緻澱粉、隱性脂肪過剩之外食環境成為誘發心血管與糖尿病元兇。智慧手錶普及率已突破 45%，物聯網生理監測數據已具備成熟基礎。
* **[But — 既有挑戰]**：MyFitnessPal 等記帳 App 繁瑣且流失率超 80%；通用 LLM (ChatGPT) 存在「營養學數值幻覺」且無即時穿戴物聯網串聯；外送地圖演算法以商業利潤推銷油炸高熱量食品，脫鉤用戶健檢紅字（高血壓禁高鈉、高尿酸避普林）。
* **[Cure — 本專案解決方案]**：提出 **NutriAgent**，一個結合臨床營養學專家思維的 **Domain AI Agent**。串聯 Google Fit 物聯網生理串流、解析健檢紅字硬邊界、檢索周邊實體外食菜單，並運用 **PyTorch 深度強化學習 (DRL)** 演進個人口味偏好。
* **[Development — 核心技術]**：
  1. **Google Fit REST API / 代謝流管線**：以分鐘級計算動態總能量消耗 (Dynamic TDEE)。
  2. **臨床醫學硬約束閘門 (Clinical Constraint Gate)**：嚴格執行 AHA/ADA/得舒(DASH) 營養醫學規則，確保違規率 0%。
  3. **PyTorch Deep Q-Network (DQN) 策略網路**：即時在線學習 (Online Learning)，平衡探索與口味適配。
  4. **地理空間 LBS 檢索**：索引台灣四大超商與連鎖便當店 500+ 餐點全營養成分。
* **[Experiments & Findings — 預期成效]**：在 5 組典型臨床表型下，達成 **100% 杜絕健檢禁忌餐點 (Zero Clinical Violation Rate)**，單餐熱量偏差控制在 $\pm 5\%$ 以內，並於 5 次互動內自適應口味偏好轉變。

---

## 🏗️ 系統架構圖 (System Architecture)

```
① 使用者情境 (外食時段、飢餓、商圈位置)
        ↓
② 多源輸入 (Google Fit 步數/熱量、健檢報告指標、GPS 坐標)
        ↓
③ 中央協同規劃代理人 (動態 TDEE 代謝計算器、狀態特徵編碼 s_t)
        ↓
④ 數據檢索與知識庫 (周邊 1km 超商/外食全營養知識庫)
        ↓
⑤ 臨床醫學硬約束閘門 (DASH 限鈉 < 700mg、低 GI、避普林、低飽和脂肪)
        ↓
⑥ 深度強化學習推薦引擎 (PyTorch DQN: Q(s, a) + 多目標加權排序)
        ↓
⑦ 決策與臨床可解釋性摘要 (Top-3 實體外食推薦 + 臨床營養依據說明)
        ↓
⑧ 呈現與閉環反饋 (Flask Web Cockpit、點選採納/太油即時更新 Q 網路)
```

---

## 📂 專案檔案結構 (Repository Layout)

```
FinalProject/
├── PROPOSAL.md                  # 完整的期末專題提案書 (含 A-F 摘要、緒論、相關文獻、三大深度問題、演算法)
├── DESIGN.md                    # 系統架構設計文件 (依據課程交接規範維護)
├── README.md                    # 本專案說明文件
├── requirements.txt             # 專案依賴套件 (PyTorch, Flask, NumPy 等)
├── .gitignore                   # Git 忽略配置
├── app.py                       # 互動式 Web Cockpit 演示伺服器 (Flask + Modern Glassmorphism UI)
├── data/
│   ├── sample_health_reports.json # 5 組真實臨床表型資料 (高血壓、糖尿病前期、痛風、健身、久坐學生)
│   └── meal_catalog.json        # 台灣外食全營養資料庫 (7-11、全家、梁社漢、Subway、健康餐盒等)
├── src/
│   ├── agent.py                 # NutriAgent 核心排程代理人
│   ├── clinical_rules.py        # 臨床營養硬約束閘門 (MNT Rules Engine)
│   ├── iot_pipeline.py          # Google Fit 物聯網生理訊號串流與動態 TDEE 計算
│   ├── recommender.py           # PyTorch Deep Q-Network (DQN) 強化學習策略模型
│   └── spatial_lbs.py           # LBS 地理空間索引與 Haversine 距離檢索
└── tests/
    └── test_agent.py            # 自動化測試套件 (臨床零違規、動態代謝縮放、DRL 梯度更新)
```

---

## 🚀 快速開始 (Quick Start)

### 1. 環境需求
* Python 3.10 以上 (支援 Python 3.10 ~ 3.14)
* 支援 Windows / macOS / Linux

### 2. 安裝套件依賴
```powershell
pip install -r requirements.txt
```

### 3. 執行自動化臨床安全與演算法測試
專案內建完整的單元與整合測試，驗證臨床硬約束零違規與 PyTorch 梯度更新：
```powershell
python -m unittest tests/test_agent.py
```
*預期輸出：*
```
.....
----------------------------------------------------------------------
Ran 5 tests in 2.3s

OK
```

### 4. 啟動互動式展示介面 (Interactive Web Cockpit)
```powershell
python app.py
```
在瀏覽器開啟 **`http://127.0.0.1:5000`**，即可體驗：
1. **切換健檢報告**：觀察高血壓第一期、糖尿病前期或痛風患者之紅字指標。
2. **切換 Google Fit 活動量**：切換久坐 (~1,850步) 與高強度訓練 (~14,200步)，觀察動態 TDEE 與當餐配額即時縮放。
3. **執行推薦**：系統自動於周邊 1km 內篩選實體餐點，並展示「剔除了多少件違規餐點（如高鈉油炸）」。
4. **即時強化學習反饋**：點擊「✔️ 採納並前往」或「🍳 太油太鹹」，介面底部的 PyTorch 策略權重將立即進行在線梯度反向傳播！

---

## 🧪 核心模組與演算法對照 (Code Implementation Mapping)

| 提案規範章節 | 對應實作檔案 | 核心類別 / 函數 | 說明 |
| :--- | :--- | :--- | :--- |
| **IoT 動態代謝計算** | `src/iot_pipeline.py` | `IoTPipeline.calculate_dynamic_budget()` | 結合 Harris-Benedict 與穿戴安全阻尼係數 ($\alpha=0.65$) |
| **臨床硬約束閘門** | `src/clinical_rules.py` | `ClinicalRulesEngine.evaluate_meal_safety()` | 嚴格過濾高血壓限鈉、高血糖低 GI、痛風避普林 |
| **LBS 空間檢索** | `src/spatial_lbs.py` | `SpatialLBSEngine.retrieve_nearby_meals()` | Haversine 地球大圓弧距離與步行時間預估 |
| **PyTorch 深度強化學習** | `src/recommender.py` | `NutriQNetwork`, `DRLRecommender` | 8維狀態+6維動作輸入，LeakyReLU MLP 預測 Q 值 |
| **中央代理人協同** | `src/agent.py` | `NutriAgent.run_recommendation()` | 串連 ①-⑧ 端到端管線，生成臨床解釋理由 |
| **即時線上閉環** | `src/agent.py` | `NutriAgent.handle_user_feedback()` | 使用者反饋驅動在線經驗回放與單步 SGD 更新 |

---

## 📄 交付文件導覽 (Deliverables)

1. **[PROPOSAL.md](PROPOSAL.md)**：包含課程要求之完整提案內容（六段式 Abstract、A-F 緒論、文獻表、五大思維模式、三大爭論、十大深度問題、帶行號 Pseudocode）。
2. **[DESIGN.md](DESIGN.md)**：包含完整系統架構、元件依賴、資料 Schema、演算法公式與評估規範。
3. **[tests/test_agent.py](tests/test_agent.py)**：可重現的自動化測試套件。

---

## 👨‍💻 作者與版權說明
本專案為「物聯網應用與資料分析」期末專案成果，採用 MIT 授權條款開源發布。
