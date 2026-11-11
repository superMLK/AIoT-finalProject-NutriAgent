# OpenSpec Change Proposal: AI Agent 接續優化協同框架
Change ID: `agentic-continuity-optimization`

## 1. Why & Motivation (The Problem)
* **AI 代理人接力斷層 (Agent Amnesia & Drift)**：當不同 AI 代理人（如 Cursor, Claude Code, Cline, Copilot 或其他大型語言模型）切換介入同一個 Repository 時，若缺乏統一的結構化提示指引與可驗證的測試基準，後續 Agent 往往會破壞原有的醫學臨床硬規則（例如將確定性過濾改寫為機率型軟提示）、寫入不可移植的絕對路徑、或是遺漏依賴，導致專案崩潰。
* **缺乏量化優化評測標準 (Lack of Objective Grounding)**：後續 Agent 在優化 DRL 策略或調整演算法時，無法客觀得知其修改是否真正降低了推論耗時、縮小了熱量預算誤差，或引發了臨床違規。

## 2. What (Proposed Solution)
* **建立萬用代理人規範文件 (`AGENTS.md`)**：提供所有主流 AI Coding Agent 通用之系統架構地圖、非協商式黃金不變量（Golden Invariants：CVR = 0%、無硬編碼絕對路徑、UTF-8 終端防呆）、OpenSpec 變更作業規範，以及 4 大預先規劃之優化軌道 (Optimization Tracks)。
* **自動化基準測試工具 (`benchmark.py`)**：提供一鍵式評測腳本，輸出結構化 `[AGENT_JSON_OUTPUT_START] ... [AGENT_JSON_OUTPUT_END]`，涵蓋 CVR、AVR、熱量 MAE、平均推論耗時與 DRL 適應靈敏度，讓任何 Agent 都能在幾秒鐘內驗證其優化成效。
* **全路徑彈性化 (`pathlib.Path`)**：所有資料載入皆以檔案自身位置向上定位至專案根目錄，徹底杜絕工作目錄不一致引發的 `FileNotFoundError`。

## 3. Scope Specification
* **In-Scope**:
  - `AGENTS.md` 全域 AI 代理人指令書。
  - `benchmark.py` 自動化機器可讀評測套件。
  - 專案所有 Python 模組相對於專案根目錄之動態路徑解析改造。
  - 4 組跨平台執行腳本 (`setup_env`, `run_demo`, `run_web`, `run_test`)。
* **Out-of-Scope**:
  - 雲端自動化持續整合 CI/CD 伺服器之外部 Webhook 配置。
