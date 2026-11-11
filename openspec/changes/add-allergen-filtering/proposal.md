# OpenSpec Change Proposal: 新增過敏食物輸入與嚴格過濾功能
Change ID: `add-allergen-filtering`

## 1. Why & Motivation (The Problem)
* **臨床醫學嚴重性**：食物過敏（Food Allergy）屬於急性免疫球蛋白 E (IgE) 媒介型超敏反應，誤食過敏原可能在數分鐘內誘發全身性蕁麻疹、喉頭水腫、支氣管痙攣甚至過敏性休克（Anaphylaxis），具有致命危險。
* **外食族資訊盲點**：外食店家常在醬汁、調味料或烹調過程中使用隱性過敏原（如沙茶醬含花生或蝦米、勾芡醬含小麥麩質、高湯使用海鮮提味）。使用者在點餐時極難單從菜名判別。
* **系統缺口**：既有 NutriAgent 聚焦於慢性病健檢指標（血壓、血糖、血脂、尿酸），尚未提供使用者「自訂過敏原清單」的輸入介面與對應的確定性安全過濾網。

## 2. What (Proposed Solution)
* **自訂過敏原輸入**：在使用者檔案與前端介面中新增「食物過敏原（Allergens）」勾選/輸入功能，支援台灣衛福部 (TFDA) 規定的常見過敏原：海鮮/魚貝甲殼類 (`seafood`/`fish`/`shellfish`)、花生/堅果 (`peanuts`/`nuts`)、麩質/小麥 (`gluten`)、蛋類 (`egg`)、奶製品 (`dairy`)、大豆 (`soy`)、芝麻 (`sesame`)。
* **臨床硬約束零容忍過濾**：在 `ClinicalRulesEngine` 中新增過敏原嚴格過濾機制。若候選餐點含有使用者宣告的任一過敏原，一律強制自候選池中剔除，達成過敏原臨床零違規（Allergen Violation Rate = 0.0%）。
* **可解釋性衛教提示**：在推薦理由與餐點卡片上標註安全過敏原標籤，或在拒絕日誌中明確記載剔除原因（例如：「排除原因：餐點含有您過敏的食材 [海鮮/甲殼類]」）。

## 3. Scope Specification
* **In-Scope**:
  - 資料庫 `data/sample_health_reports.json` 與 `data/meal_catalog.json` 擴充過敏原欄位。
  - `src/clinical_rules.py` 實作別名關聯（例如使用者勾選 `seafood`，能自動比對 `fish`、`shrimp`、`shellfish`）。
  - `src/agent.py` 整合動態過敏原參數傳遞與過濾診斷。
  - `app.py` 新增前端即時過敏原勾選方塊與 API 串接。
  - `tests/test_agent.py` 新增過敏原隔離測試案例。
* **Out-of-Scope**:
  - 工廠共用產線之「微量微痕交叉污染 (Trace cross-contact)」分子檢測。
