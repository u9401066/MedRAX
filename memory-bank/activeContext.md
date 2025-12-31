# Active Context

## Current Goals

- ## 當前工作焦點
- ### 資料流邏輯分析完成 ✅
- **原 MedRAX 架構**：
- ```
- User → Gradio → GPT-4o(bind_tools) → execute_tools() → GPT-4o(整合) → Response
- ↑                      │
- └──────────────────────┘
- (LangGraph 循環：LLM 看到工具結果後再生成最終回應)
- ```
- **MCP 架構**：
- ```
- User → Copilot → MCP Server → Tool Wrappers → DL Models
- ↓
- 結構化結果 + Base64
- ↓
- Copilot 整合 ← 關鍵：Copilot 負責臨床推理！
- ↓
- Markdown 回應
- ```
- ### 關鍵發現
- 1. **職責等價**：原架構中 GPT-4o 負責整合 = MCP 架構中 Copilot 負責整合
- 2. **需補充 MCP Prompt**：確保 Copilot 知道如何進行臨床推理
- 3. **圖像處理**：image_path → image_id + Base64 返回
- ### 文檔更新
- - `docs/MCP_TOOLS_MAPPING.md` - 新增資料流對照圖
- - 9 個 LangChain Tools → MCP Tools 映射完成
- ### 下一步
- - Git commit & push
- - 開始 v0.1.4-alpha FastMCP 實作

## Current Blockers

- None yet