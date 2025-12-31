# Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-12-31 | MCP 架構中，Copilot 負責整合工具結果並生成臨床解釋（等同原架構中 GPT-4o 的角色） | 原 MedRAX 使用 LangGraph 循環：process_request → execute_tools → process_request，讓 LLM 看到工具結果後再生成最終回應。在 MCP 架構中，這個職責由 GitHub Copilot 承擔。需要補充 MCP Prompt 以確保臨床推理品質。 |
