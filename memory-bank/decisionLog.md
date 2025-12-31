# Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-12-31 | MCP 架構中，Copilot 負責整合工具結果並生成臨床解釋（等同原架構中 GPT-4o 的角色） | 原 MedRAX 使用 LangGraph 循環：process_request → execute_tools → process_request，讓 LLM 看到工具結果後再生成最終回應。在 MCP 架構中，這個職責由 GitHub Copilot 承擔。需要補充 MCP Prompt 以確保臨床推理品質。 |
| 2025-12-31 | 採用 Agent Abstraction Layer 設計，支援 Copilot/Cline/Claude/Custom 等多種 Agent 無縫切換 | 降低對單一 Agent 的依賴風險，提高架構靈活性，為未來獨立部署和 FHIR 整合鋪路 |
| 2025-12-31 | 規劃獨立 Web 前端 (v0.1.8) 與 FHIR 整合 (v0.1.9) 作為長期目標 | 最終目標是不依賴 VS Code 的獨立醫學影像分析平台，透過 FHIR 實現與 EHR 系統的互通 |
| 2025-12-31 | MCP Server 採用 DDD 四層架構實作，使用 FastMCP SDK | DDD 架構確保關注點分離，Domain 層定義核心實體和協議，Infrastructure 層包裝 DL 模型，Application 層協調服務，Presentation 層暴露 MCP 工具 |
