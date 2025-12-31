# CLAUDE.md - Claude Code 專案指引

> 此文件為 Claude Code（Anthropic 的 AI 編程助手）提供 MedRAX 專案上下文。

---

## 專案概述

**MedRAX** - Medical Reasoning Agent for Chest X-ray

這是一個醫學 AI 推理代理框架，旨在：
- 整合最先進的醫學影像分析工具
- 透過 LangChain/LangGraph 編排複雜推理流程
- 提供統一的醫學影像查詢接口
- 支援本地和雲端部署

### 技術棧
- **LLM**: GPT-4o with Vision
- **框架**: LangChain, LangGraph
- **前端**: Gradio（生產級）
- **醫學工具**: CheXagent, LLaVA-Med, MedSAM, PSPNet, Maira-2, SwinV2, DenseNet-121, RoentGen
- **影像處理**: DICOM I/O, 自定義可視化工具

## 法規層級

```
CONSTITUTION.md                      ← 最高原則（不可違反）
  │
  ├─ .github/bylaws/                 ← 細則規範
  │  ├── ddd-architecture.md         ← DDD 架構規範
  │  ├── git-workflow.md             ← Git 工作流
  │  ├── memory-bank.md              ← 專案記憶管理
  │  └── python-environment.md       ← Python 環境管理
  │
  └─ .claude/skills/*/SKILL.md       ← 具體操作程序
```

## 核心原則

### 1. DDD 架構遵循
- **Domain**: 醫學推理邏輯（diagnosis、reasoning）
- **Application**: Agent 編排、Query 處理
- **Infrastructure**: 工具包裝、DICOM 處理、外部服務調用
- **Presentation**: Gradio UI、REST API

### 2. 工具隔離原則
每個醫學工具 (CheXagent, MedSAM, etc) 必須：
1. 有獨立的 Service 包裝層
2. 通過明確的接口與 Domain Logic 互動
3. 所有 I/O 操作集中在 Infrastructure Layer

### 3. Memory Bank 同步
每次編碼前後都要：
1. 更新 `activeContext.md` - 當前工作焦點
2. 更新 `progress.md` - 完成的任務
3. 更新 `decisionLog.md` - 重大決策
4. 更新 `architect.md` - 架構變更
  ├── .github/bylaws/    ← 子法（細則規範）
  │     ├── ddd-architecture.md
  │     ├── git-workflow.md
  │     └── memory-bank.md
  │
  └── .claude/skills/    ← 實施細則（操作程序）
```

## 核心原則

### 0. 開發哲學 💡
> **「想要寫文件的時候，就更新 Memory Bank 吧！」**
> 
> **「想要零散測試的時候，就寫測試檔案進 tests/ 資料夾吧！」**

- 不要另開檔案寫筆記，直接寫進 Memory Bank
- 今天的零散測試，就是明天的回歸測試

### 1. DDD 架構
- Domain Layer 不依賴外部
- DAL (Data Access Layer) 必須獨立
- 使用 Repository Pattern
- 參見：`.github/bylaws/ddd-architecture.md`

### 2. Python 環境（uv 優先）
```bash
# 初始化
uv venv && uv sync --all-extras

# 安裝依賴
uv add package-name
uv add --dev pytest ruff mypy
```
- 參見：`.github/bylaws/python-environment.md`

### 3. Memory Bank 同步
每次重要操作必須更新：
- `memory-bank/progress.md` - 進度追蹤
- `memory-bank/activeContext.md` - 當前焦點
- `memory-bank/decisionLog.md` - 重要決策

### 4. Git 工作流
提交前執行檢查清單：
1. Memory Bank 同步
2. README 更新（如需要）
3. CHANGELOG 更新
4. ROADMAP 標記

## 可用 Skills

| Skill | 用途 |
|-------|------|
| `git-precommit` | Git 提交前編排器 |
| `ddd-architect` | DDD 架構輔助 |
| `code-refactor` | 主動重構與模組化 |
| `memory-updater` | Memory Bank 同步 |
| `memory-checkpoint` | 記憶檢查點（Summarize 前外部化） |
| `readme-updater` | README 智能更新 |
| `changelog-updater` | CHANGELOG 自動更新 |
| `roadmap-updater` | ROADMAP 狀態追蹤 |
| `code-reviewer` | 程式碼審查 |
| `test-generator` | 測試生成（Unit/Integration/E2E） |
| `project-init` | 專案初始化 |

## 💸 Memory Checkpoint 規則

### 主動觸發時機
- 對話超過 **10 輪** 時，主動建議 checkpoint
- 完成 **重大功能** 後，主動執行 checkpoint
- 使用者說要 **離開/等等繼續** 時，主動執行 checkpoint

### Checkpoint 內容必須包含
- 具體檔案路徑
- 變更摘要
- 下一步計畫
- 重要決策（如有）

### 觸發指令
```
「記憶檢查點」 / 「checkpoint」 / 「存檔」
「保存記憶」 / 「sync memory」
```

## 常用指令

```
「準備 commit」       → 執行完整提交流程
「快速 commit」       → 只同步 Memory Bank
「建立新功能 X」      → 生成 DDD 結構
「review 程式碼」     → 程式碼審查
「更新 memory bank」  → 同步專案記憶
```

## 目錄結構約定

```
src/
├── Domain/           # 核心領域（無外部依賴）
├── Application/      # 應用層（用例編排）
├── Infrastructure/   # 基礎設施（DAL、外部服務）
└── Presentation/     # 呈現層（API、UI）
```

## 注意事項

- 修改程式碼前先更新規格文檔
- 程式碼是文檔的「編譯產物」
- 遵循 Conventional Commits 格式
- 使用繁體中文回應
