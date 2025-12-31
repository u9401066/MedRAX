# MedRAX Plus Roadmap

> Advanced Multi-Modal Medical Reasoning Agent - Development Roadmap

## Current Status

**Latest Release**: v0.1.0 (Original MedRAX + Constitutional Framework)
- ✅ CXR analysis tools fully functional
- ✅ Constitutional AI framework integrated
- ✅ Memory Bank system in place
- ✅ 13 Claude Skills for development automation
- ❌ EKG support not yet implemented
- ❌ LangGraph modernization pending
- ❌ Interactive UI features not complete
- ❌ MCP/Copilot integration not started

---

## MedRAX2 新功能參考 (bowang-lab/MedRAX2)

> 原團隊後續作品，232 commits ahead of original。我們參考但採用更好的架構方案。

| MedRAX2 新增 | 說明 | MedRAX Plus 策略 |
|-------------|------|------------------|
| **MedSAM2** | 基於 Meta SAM2 的交互式分割 | ✅ 採用，整合至 v0.1.2 |
| **MedGemma VQA** | Google 4B 醫學 VQA 模型 | 🤔 評估中，可能作為備選 VQA |
| **ArcPlus Classifier** | SwinTransformer，52+ 病理類別 | 🤔 評估是否優於 DenseNet-121 |
| **PythonSandboxTool** | Pyodide + Deno 沙盒執行 | ⏭️ 低優先，MCP Server 可處理 |
| **LangGraph** | 狀態機架構 | ✅ 採用，但用 DDD 架構包裝 |
| **WebBrowser/DuckDuckGo** | 網頁搜尋工具 | ⏭️ 低優先，聚焦醫學影像 |
| **MedicalRAGTool** | Pinecone + Cohere RAG | 🤔 v0.1.5+ 考慮 |
| **Multi-LLM** | OpenAI, Gemini, Grok, OpenRouter | ✅ 參考，保持模型靈活性 |

**我們的差異化優勢**（MedRAX2 沒有）：
- 🫀 **EKG 多模態** - 心電圖分析與 CXR 聯合推理
- 🔌 **MCP Server + Copilot** - VS Code 原生整合
- 🏛️ **DDD 架構治理** - 清晰的層次分離
- 📜 **Constitutional Framework** - AI 治理與開發自動化

---

## Phase 1: Multi-Modal Foundation (v0.1.1) - Q1 2025

### Objectives
Extend MedRAX with EKG/ECG analysis capabilities and multi-modal joint reasoning.

### Tasks
- [ ] **EKG Signal Processing**
  - Implement R-peak detection algorithm
  - Add Heart Rate Variability (HRV) analysis
  - Create signal quality assessment (ECG-SQI)
  - Support 12-lead ECG input formats

- [ ] **EKG Classification Models**
  - Integrate ResNet-ECG for arrhythmia classification
  - Add Transformer-based anomaly detection
  - Implement ArrhythmiaNet for specific patterns
  - Create ECG pattern matching database

- [ ] **EKG Report Generation**
  - Implement ECG-BERT for clinical report generation
  - Create structured EKG finding templates
  - Add measurement reporting (HR, PR, QRS, QT, ST)
  - Generate confidence scores for findings

- [ ] **Multi-Modal Joint Reasoning**
  - Extend agent prompts to handle CXR + EKG context
  - Create clinical scenario examples (pneumonia + AFib, etc.)
  - Implement risk assessment for cardiopulmonary conditions
  - Add treatment interaction warnings

- [ ] **Documentation & Examples**
  - Create EKG analysis example notebooks
  - Add clinical use case examples
  - Update API documentation
  - Add EKG tool selection documentation

### Success Criteria
- ✅ EKG analysis produces clinically valid outputs
- ✅ Multi-modal analysis working for 5+ clinical scenarios
- ✅ Test coverage >= 80% for new EKG modules
- ✅ Benchmark on EKG dataset (e.g., PhysioNet)

### Estimated Timeline
**2-3 weeks** | Dependencies: None

---

## Phase 2: Architecture Modernization (v0.1.2) - Q1-Q2 2025

### Objectives
Modernize agent architecture using LangGraph and implement state-based reasoning.

### Tasks
- [ ] **LangGraph Migration**
  - Rewrite agent.py using LangGraph StateGraph
  - Implement conditional routing (CXR/EKG/Combined paths)
  - Create multi-node workflow (process → route → execute → synthesize)
  - Add state persistence and checkpoint management

- [ ] **State Management**
  - Define MedicalReasoningState TypedDict with:
    - Query and uploaded images
    - Query type routing
    - CXR findings and reports
    - EKG features and classifications
    - Combined context and recommendations
    - Reasoning traces for explainability
  - Implement state transition logic
  - Add state validation

- [ ] **Modern Tool Integration**
  - Implement Tool Use Protocol (Anthropic/OpenAI standard)
  - Convert all tools to JSON Schema format
  - Add tool input validation
  - Implement streaming tool responses

- [ ] **Query Router**
  - Create NLU classifier (CXR vs EKG vs Combined)
  - Add heuristic fallback rules
  - Implement confidence-based routing
  - Add user query refinement prompts

- [ ] **Reasoning Trace System**
  - Log all decision points
  - Track tool calls and results
  - Create human-readable reasoning explanations
  - Implement debug mode for detailed traces

### MedRAX2 參考
> MedRAX2 也採用 LangGraph，但我們額外加入 DDD 架構和 Tool Use Protocol 標準化。

### Success Criteria
- ✅ LangGraph-based agent handles all v0.1.0 CXR tasks
- ✅ Routing accuracy >= 95% on test set
- ✅ Reasoning traces are informative and correct
- ✅ State machine is deterministic and testable
- ✅ Performance >= v0.1.0 (no regression)

### Estimated Timeline
**3 weeks** | Dependencies: Phase 1 completion

---

## Phase 2.5: Interactive UI Enhancement (v0.1.3) - Q2 2025

### Objectives
Implement interactive region-aware UI with spatial context understanding.

### Tasks
- [ ] **Annotation Canvas**
  - Integrate Gradio Canvas component
  - Support multiple annotation types:
    - Bounding boxes (rectangular regions)
    - Circles (focal areas)
    - Free-form polygons (complex regions)
  - Implement coordinate tracking
  - Add annotation metadata (labels, questions)

- [ ] **Region-Focused Analysis**
  - Extract ROI (Region of Interest) from marked areas
  - Implement region-specific feature extraction
  - Create focused prompts that mention marked regions
  - Add spatial descriptors (location, size, relationships)

- [ ] **Multi-Modal Input Support**
  - Add voice input for queries (speech-to-text)
  - Support text queries for marked regions
  - Implement camera capture for live input
  - Add historical image comparison

- [ ] **Visual Feedback**
  - Display model predictions on canvas
  - Show confidence scores per region
  - Visualize heatmaps for attention areas
  - Add bounding boxes for detected findings

- [ ] **Responsive Design**
  - Optimize for desktop and tablet
  - Implement touch-friendly controls
  - Add keyboard shortcuts
  - Create dark/light mode support

### Success Criteria
- ✅ Canvas annotations render correctly
- ✅ Model correctly interprets marked regions
- ✅ UI is responsive and intuitive
- ✅ User testing shows 80%+ satisfaction
- ✅ Loading time < 2 seconds for marked region analysis

### Estimated Timeline
**1-2 weeks** | Dependencies: Phase 2 completion

---

## Phase 3: Multi-Interface Deployment (v0.1.4) - Q2-Q3 2025

### Objectives
Enable deployment across multiple platforms using FastMCP + DDD architecture.

See [MCP_SERVER_DESIGN.md](MCP_SERVER_DESIGN.md) for detailed architecture.

### 3A: FastMCP Server Foundation (v0.1.4-alpha) - 2 weeks
**Objectives**: Build DDD-based MCP Server with FastMCP

- [ ] **FastMCP 伺服器骨架**
  - Initialize FastMCP application
  - Create tool registration pattern
  - Implement request/response marshalling
  - Setup error handling framework

- [ ] **初始 Tools 實現** (3 個)
  - `analyze_cxr`: CXR 影像分析
  - `analyze_ekg`: EKG 信號分析  
  - `combined_analysis`: 聯合心肺分析
  - Tool input validation
  - Response formatting

- [ ] **Application Layer**
  - CXR Analysis Service (Tool orchestration)
  - EKG Analysis Service
  - Fusion Service (Multi-modal)
  - DTO definitions
  - Service-to-Tool mapping

- [ ] **Docker 容器化**
  - Dockerfile with CUDA support
  - Docker-compose for local dev
  - Model weight mounting
  - Health check endpoints

**Success Criteria**:
- ✅ FastMCP server starts without errors
- ✅ 3 tools callable from MCP client
- ✅ Request/response cycle works end-to-end
- ✅ Containerized deployment works locally

### 3B: DDD Infrastructure Layer (v0.1.4-beta) - 2 weeks
**Objectives**: Complete DDD implementation for production

> 💡 **vs MedRAX2**: MedRAX2 無 DDD 架構，工具直接耦合。我們的分層設計更易維護。

- [ ] **Domain Models**
  - CXRFinding (findings, pathologies, locations)
  - EKGFinding (measurements, classifications, reports)
  - ClinicalAssessment (aggregated reasoning)
  - Value Objects (Confidence, Location, etc)

- [ ] **Domain Services**
  - CXRAnalyzer (medical reasoning for CXR)
  - EKGAnalyzer (medical reasoning for EKG)
  - ClinicalReasoner (joint analysis)
  - Pure business logic (no external dependencies)

- [ ] **Infrastructure Tool Wrappers**
  - CheXagentWrapper (classification)
  - MedSAMWrapper (segmentation)
  - LLavaMedWrapper (VQA)
  - ResNetECGWrapper (ECG classification)
  - ECGSQIWrapper (signal quality)
  - All wrappers with caching

- [ ] **Repository Pattern**
  - ImageRepository (DICOM/PNG storage)
  - SignalRepository (ECG storage)
  - CacheRepository (Model cache)
  - Abstract base classes

- [ ] **Comprehensive Testing**
  - Unit tests for domain services (target 85%+ coverage)
  - Integration tests for wrappers
  - Mock models for fast testing
  - Test data fixtures

**Success Criteria**:
- ✅ All domain models well-defined
- ✅ Clear separation of concerns (DDD layers)
- ✅ Tool wrappers pass integration tests
- ✅ Test coverage >= 85%
- ✅ Performance acceptable (< 5s for inference)

### 3C: VS Code Copilot Integration (v0.1.4-rc1) - 1-2 weeks
**Objectives**: Integrate MedRAX with Copilot via MCP

> 💡 **vs MedRAX2**: MedRAX2 只有 Gradio UI。我們提供 MCP + Copilot 原生整合。

- [ ] **VS Code 擴展骨架**
  - Extension manifest (package.json)
  - Activation events
  - Configuration schema
  - Extension commands

- [ ] **Copilot Participant 實現**
  - @medrax command handler
  - Chat interface integration
  - Message formatting
  - Command palette registration

- [ ] **功能實現**
  - Image attachment parsing
  - Base64 encoding for transmission
  - Region marking support (from Copilot)
  - Response streaming
  - Error display

- [ ] **使用者體驗**
  - Progress indicators
  - Streaming responses
  - Image preview in chat
  - Formatting and styling
  - Accessibility features

- [ ] **文檔和示例**
  - Extension README
  - Usage examples
  - Configuration guide
  - Troubleshooting section

**Success Criteria**:
- ✅ Extension installs cleanly from VS Code marketplace
- ✅ @medrax commands work in Copilot chat
- ✅ Image attachments process correctly
- ✅ Results display properly formatted
- ✅ User can understand the analysis

### 3D: Multi-Interface Orchestration (v0.1.4-rc2) - 1 week
**Objectives**: Unified interface for Gradio + MCP + Copilot

- [ ] **統一的 Agent 層**
  - Single MedRAX agent core
  - Interface adapters (Gradio, MCP, Copilot)
  - Request/response normalization
  - Shared state management

- [ ] **介面適配層**
  - GradioAdapter (web UI)
  - MCPAdapter (MCP protocol)
  - CopilotAdapter (VS Code integration)
  - Common request validation

- [ ] **Configuration Management**
  - Model selection per interface
  - Tool availability configuration
  - Performance tuning per interface
  - Feature flags

- [ ] **Monitoring & Observability**
  - Structured logging
  - Performance metrics per interface
  - Error tracking
  - Usage analytics

**Success Criteria**:
- ✅ Same agent logic across all 3 interfaces
- ✅ Configuration management works
- ✅ Metrics collection functional
- ✅ No interface regressions

### 3E: Production Optimization (v0.1.4) - 1-2 weeks
**Objectives**: Performance and reliability hardening

- [ ] **性能最佳化**
  - Model caching strategies
  - Batch processing where applicable
  - Image preprocessing optimization
  - Latency profiling and reduction
  - Target: CXR analysis < 3s, EKG < 2s

- [ ] **可靠性改進**
  - Retry mechanisms for transient failures
  - Graceful degradation
  - Circuit breaker patterns
  - Rate limiting

- [ ] **安全加固**
  - Input validation (image size, format)
  - Signal validation (EKG length, sampling rate)
  - API key management
  - HTTPS/TLS configuration

- [ ] **部署最佳實踐**
  - Database for result caching
  - Load balancing
  - Auto-scaling configuration
  - Backup and recovery

**Success Criteria**:
- ✅ Performance meets SLA (CXR < 3s)
- ✅ 99.5% uptime in staging
- ✅ Security audit passed
- ✅ Deployment documented

### Timeline Summary for Phase 3
```
v0.1.4-alpha: FastMCP Foundation     [████░░░░░░] 2 weeks
v0.1.4-beta:  DDD Infrastructure     [████░░░░░░] 2 weeks
v0.1.4-rc1:   Copilot Integration    [███░░░░░░░] 1-2 weeks
v0.1.4-rc2:   Multi-Interface        [██░░░░░░░░] 1 week
v0.1.4:       Production Ready       [███░░░░░░░] 1-2 weeks
                                      ────────────
                            Total:    [7-9 weeks]
```

---

## Phase 3 (Original): Multi-Interface Deployment (v0.1.4) - Q2-Q3 2025

> ⚠️ 此為原始規劃，已被上方詳細拆分取代。保留供參考。

### Objectives
Enable deployment across multiple platforms (Gradio, MCP, VS Code).

### 3A: MCP Server Implementation
- [ ] **MCP Server Framework**
  - Wrap MedRAX agent as MCP server
  - Implement tool registration protocol
  - Add resource management
  - Create error handling and fallbacks

- [ ] **Tools as Resources**
  - Expose `cxr_analysis` tool
  - Expose `ekg_analysis` tool
  - Expose `clinical_decision_support` tool
  - Expose `image_grounding` tool
  - Add configuration resources

- [ ] **Claude Integration Testing**
  - Test with Claude 3.5 (native MCP support)
  - Verify tool calling flow
  - Add usage examples
  - Document API contract

- [ ] **Documentation**
  - Write MCP server README
  - Create integration guide
  - Add troubleshooting section
  - Provide example prompts

### 3B: VS Code Copilot Extension
- [ ] **Extension Development**
  - Create VS Code extension scaffold
  - Implement Copilot Participant interface
  - Add @medrax command handler
  - Create extension configuration

- [ ] **Features**
  - Image attachment support
  - Chat message rendering
  - File browser integration
  - Inline result display

- [ ] **Packaging & Distribution**
  - Build extension package
  - Publish to VS Code marketplace
  - Create installation guide
  - Set up update mechanism

### 3C: Deployment Management
- [ ] **Multi-Interface Router**
  - Unified agent interface
  - Request parsing per interface
  - Response formatting per output format
  - Logging and monitoring

- [ ] **Configuration**
  - Environment-based settings
  - Multi-interface configuration
  - Model selection
  - Tool availability per interface

- [ ] **Documentation**
  - Deployment guide for each interface
  - Architecture diagram
  - Configuration reference
  - Troubleshooting guide

### Success Criteria
- ✅ MCP server passes Claude integration tests
- ✅ VS Code extension installs cleanly
- ✅ @medrax commands work in Copilot chat
- ✅ All three interfaces share same agent logic
- ✅ Documentation is complete and tested

### Estimated Timeline
**3-4 weeks** | Dependencies: Phase 2 completion

---

## Phase 4: Production Hardening (v0.1.5) - Q3 2025

### Objectives
Ensure production-grade reliability, performance, and security.

### Tasks
- [ ] **Testing & Quality**
  - Comprehensive unit test suite (targets 85%+ coverage)
  - Integration tests for each interface
  - End-to-end workflow tests
  - Performance benchmarking and optimization

- [ ] **Security**
  - Input validation for all tool parameters
  - API key management best practices
  - DICOM/EKG data privacy considerations
  - Rate limiting and usage tracking

- [ ] **Monitoring & Observability**
  - Structured logging (JSON format)
  - Performance metrics (latency, throughput)
  - Error tracking and alerting
  - Usage analytics

- [ ] **Documentation**
  - API reference documentation
  - Deployment guides
  - Security best practices
  - Troubleshooting guides

- [ ] **Release Management**
  - Semantic versioning
  - CHANGELOG maintenance
  - Migration guides for breaking changes
  - Release notes

### Success Criteria
- ✅ Test coverage >= 85%
- ✅ All documented APIs work as specified
- ✅ No critical security vulnerabilities
- ✅ Documentation is comprehensive and accurate
- ✅ Performance meets SLA targets

### Estimated Timeline
**2-3 weeks** | Dependencies: Phase 3 completion

---

## Phase 5: Advanced Features (v0.1.6+) - Future

### Potential Enhancements (含 MedRAX2 參考) (含 MedRAX2 參考)

**原規劃功能**：
- **Multi-Hospital Integration**: FHIR/HL7 standards
- **Collaborative Analysis**: Multiple clinicians simultaneously
- **Longitudinal Analysis**: Patient history comparison
- **Mobile App**: Native iOS/Android applications
- **Model Fine-Tuning**: Custom models for specific institutions
- **Explainability Enhancement**: SHAP/LIME integration
- **Real-Time Alerts**: Abnormal finding notifications
- **Integration with EHR**: Seamless clinical workflow integration

**參考 MedRAX2 的潛在功能**：
- **MedGemma VQA**: Google 的 4B 醫學 VQA 模型，可作為 CheXagent 備選
- **ArcPlus Classifier**: SwinTransformer 分類器，52+ 病理類別，評估替代 DenseNet-121
- **MedicalRAGTool**: Pinecone + Cohere RAG，用於醫學知識檢索增強
- **Multi-LLM Support**: OpenRouter 整合開源模型、本地 LLM (Ollama) 支援
- **WebBrowser/Search Tools**: 可選的網頁搜尋輔助（低優先）

---

## Phase 6: Agent Abstraction Layer (v0.1.7) - Future

### 🎯 Vision
**實現 Agent 無關設計**：MCP Server 可與任意 Agent（Copilot、Cline、Claude Desktop、自定義）無縫協作。

### Objectives
建立 Agent 抽象層，使 MedRAX Plus 核心功能與具體 Agent 實現解耦。

### Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                    Agent Abstraction Layer                      │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │
│  │   Copilot   │  │    Cline    │  │   Claude    │  │ Custom  │ │
│  │   Adapter   │  │   Adapter   │  │   Adapter   │  │ Adapter │ │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └────┬────┘ │
│         │                │                │               │      │
│         └────────────────┴────────────────┴───────────────┘      │
│                              │                                   │
│                    ┌─────────▼─────────┐                        │
│                    │  Unified Agent    │                        │
│                    │    Interface      │                        │
│                    │  (AgentProtocol)  │                        │
│                    └─────────┬─────────┘                        │
└──────────────────────────────┼──────────────────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │    MCP Server       │
                    │  (FastMCP + DDD)    │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  MedRAX Backend     │
                    │  (Domain Services)  │
                    └─────────────────────┘
```

### Tasks
- [ ] **Agent Protocol Definition**
  - 定義 `AgentProtocol` 抽象介面
  - 標準化 Tool Call/Response 格式
  - 定義 Context 傳遞規範
  - 定義錯誤處理機制

- [ ] **Adapter Implementations**
  - `CopilotAdapter`: GitHub Copilot MCP 整合
  - `ClineAdapter`: Cline (VS Code extension) 整合
  - `ClaudeAdapter`: Claude Desktop MCP 整合
  - `OpenAIAdapter`: OpenAI Function Calling 相容
  - `CustomAdapter`: 自定義 Agent 範本

- [ ] **Configuration System**
  - Agent 選擇配置 (`medrax.agent.type`)
  - 動態 Agent 切換
  - Agent 特定參數配置
  - Fallback 機制

- [ ] **Testing & Compatibility**
  - Agent 相容性測試套件
  - Protocol 合規性驗證
  - 跨 Agent 行為一致性測試

### Agent Comparison Matrix
| Feature | Copilot | Cline | Claude | Custom |
|---------|---------|-------|--------|--------|
| MCP Support | ✅ Native | ✅ via config | ✅ Native | Depends |
| VS Code Integration | ✅ Built-in | ✅ Extension | ❌ | Depends |
| Offline Mode | ❌ | ✅ Possible | ❌ | ✅ |
| Custom Prompts | Limited | ✅ Full | ✅ Full | ✅ Full |
| Multi-Model | ❌ | ✅ | ❌ | ✅ |

### Success Criteria
- ✅ 支援至少 3 種 Agent（Copilot、Cline、Claude）
- ✅ Agent 切換無需修改核心程式碼
- ✅ 所有 Agent 獲得相同的醫學推理結果
- ✅ 提供 CustomAdapter 範本與文檔

### Estimated Timeline
**4-5 weeks** | Dependencies: Phase 3 (MCP Server) completion

---

## Phase 7: Standalone Web Interface (v0.1.8) - Future

### 🎯 Vision
**獨立部署能力**：MedRAX Plus 可作為獨立 Web 應用運行，不依賴 VS Code 或特定 Agent。

### Objectives
建立獨立的 Web 前端，直接與 MCP Server/Backend 通訊。

### Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                    Standalone Web Interface                     │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    React/Vue Frontend                     │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐ │   │
│  │  │   Chat UI   │ │ Image View  │ │ File Management     │ │   │
│  │  │  (Medical   │ │ (DICOM/EKG  │ │ (Upload/Download/   │ │   │
│  │  │   Query)    │ │  Render)    │ │  History)           │ │   │
│  │  └─────────────┘ └─────────────┘ └─────────────────────┘ │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐ │   │
│  │  │  Analysis   │ │   Report    │ │ Patient Dashboard   │ │   │
│  │  │  Results    │ │  Generator  │ │ (via FHIR)          │ │   │
│  │  └─────────────┘ └─────────────┘ └─────────────────────┘ │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                    ┌─────────▼─────────┐                        │
│                    │   REST/GraphQL    │                        │
│                    │      API          │                        │
│                    └─────────┬─────────┘                        │
└──────────────────────────────┼──────────────────────────────────┘
                               │
              ┌────────────────┴────────────────┐
              │                                  │
    ┌─────────▼─────────┐            ┌──────────▼──────────┐
    │   MCP Server      │            │   FHIR Client       │
    │  (Tool Gateway)   │            │  (EHR Integration)  │
    └─────────┬─────────┘            └──────────┬──────────┘
              │                                  │
    ┌─────────▼─────────┐            ┌──────────▼──────────┐
    │  MedRAX Backend   │            │   FHIR Server       │
    │ (Domain Services) │            │  (Epic/Cerner/etc)  │
    └───────────────────┘            └─────────────────────┘
```

### Tasks
- [ ] **Frontend Development**
  - React/Vue + TypeScript 前端框架
  - Medical Chat UI 組件
  - DICOM/EKG 影像檢視器（Cornerstone.js）
  - 檔案管理介面（上傳、下載、歷史記錄）
  - 分析結果可視化

- [ ] **API Layer**
  - REST API Gateway（FastAPI/Express）
  - WebSocket 支援（即時更新）
  - Session 管理
  - 權限控制（RBAC）

- [ ] **Authentication**
  - OAuth 2.0 / OIDC 整合
  - 院內 SSO 支援
  - API Key 認證（服務對服務）

- [ ] **Deployment Options**
  - Docker Compose（單機部署）
  - Kubernetes Helm Chart
  - 雲端部署（AWS/GCP/Azure）

### Success Criteria
- ✅ Web 前端可獨立運行（不需 VS Code）
- ✅ 支援 DICOM/EKG 檔案上傳與檢視
- ✅ 提供完整的醫學影像分析工作流
- ✅ Docker 一鍵部署

### Estimated Timeline
**6-8 weeks** | Dependencies: Phase 6 (Agent Abstraction) completion

---

## Phase 8: FHIR Integration (v0.1.9) - Future

### 🎯 Vision
**醫療系統互通**：透過 FHIR 標準與醫院 EHR 系統整合，實現病患資料自動化檢索與回寫。

### Objectives
實現 FHIR R4 標準整合，支援主流 EHR 系統（Epic、Cerner、Meditech）。

### Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                      FHIR Integration Layer                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    FHIR Client Service                    │  │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐  │  │
│  │  │  Patient    │ │  Imaging    │ │  Diagnostic Report  │  │  │
│  │  │  Retrieval  │ │  Study      │ │  (Write-back)       │  │  │
│  │  │  (R4)       │ │  (ImagingStudy)│                     │  │  │
│  │  └─────────────┘ └─────────────┘ └─────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              │                                   │
│         ┌────────────────────┼────────────────────┐             │
│         │                    │                    │             │
│  ┌──────▼──────┐     ┌───────▼───────┐    ┌──────▼──────┐      │
│  │    Epic     │     │    Cerner     │    │  Meditech   │      │
│  │   Adapter   │     │    Adapter    │    │   Adapter   │      │
│  └──────┬──────┘     └───────┬───────┘    └──────┬──────┘      │
│         │                    │                    │             │
└─────────┼────────────────────┼────────────────────┼─────────────┘
          │                    │                    │
   ┌──────▼──────┐     ┌───────▼───────┐    ┌──────▼──────┐
   │ Epic FHIR   │     │ Cerner FHIR   │    │ Meditech    │
   │   Server    │     │   Server      │    │ FHIR Server │
   └─────────────┘     └───────────────┘    └─────────────┘
```

### FHIR Resources Mapping
| MedRAX Concept | FHIR Resource | Operations |
|----------------|---------------|------------|
| Patient Info | `Patient` | Read |
| X-Ray Images | `ImagingStudy` | Read, Search |
| EKG Data | `Observation` (category: vital-signs) | Read |
| Analysis Report | `DiagnosticReport` | Create, Read |
| Findings | `Observation` (category: imaging) | Create |
| AI Annotations | `Media` + `Annotation` | Create |

### Tasks
- [ ] **FHIR Client Implementation**
  - FHIR R4 client library 整合（fhirclient/hapi-fhir）
  - OAuth 2.0 SMART on FHIR 認證
  - Patient 資源讀取
  - ImagingStudy 查詢與 WADO-RS 整合

- [ ] **EHR Adapters**
  - Epic MyChart/Hyperspace 整合
  - Cerner Millennium 整合
  - 通用 FHIR Server 支援

- [ ] **Data Synchronization**
  - 影像自動導入（FHIR → MedRAX）
  - 分析報告回寫（MedRAX → FHIR DiagnosticReport）
  - 病歷脈絡自動帶入

- [ ] **Privacy & Compliance**
  - HIPAA 合規審計日誌
  - PHI 資料處理規範
  - 同意管理（Consent resource）
  - 資料最小化原則

### Success Criteria
- ✅ 支援 FHIR R4 Patient/ImagingStudy 讀取
- ✅ 至少整合一個主流 EHR（Epic 或 Cerner）
- ✅ 分析報告可回寫為 DiagnosticReport
- ✅ 通過 SMART on FHIR 合規測試

### Estimated Timeline
**8-10 weeks** | Dependencies: Phase 7 (Web Interface) completion

---

## Long-Term Vision (v0.2.x+)

### 🚀 Ultimate Goals
1. **Multi-Modal Medical AI Platform**
   - CXR + EKG + CT + MRI 全模態支援
   - 跨模態關聯分析

2. **Real-Time Clinical Decision Support**
   - 即時異常通知
   - 臨床指引整合

3. **Federated Learning**
   - 跨院所模型聯合訓練
   - 隱私保護學習

4. **Regulatory Compliance**
   - FDA 510(k) / CE Mark 認證路徑
   - 臨床驗證研究設計

---

## Implementation Strategy

### Development Workflow
1. **Planning**: Document feature/bug details in GitHub Issues
2. **Design**: Update architectural docs if needed
3. **Implementation**: Create feature branch
4. **Testing**: Add tests before merging (TDD recommended)
5. **Review**: Code review using Constitutional Framework
6. **Documentation**: Update README, API docs, examples
7. **Deployment**: Version bump, CHANGELOG update, tag release

### Branching Model
```
main (stable releases)
  ├── v0.1.1-ekg-support (Phase 1)
  ├── v0.1.2-langgraph (Phase 2)
  ├── v0.1.3-ui-enhancement (Phase 2.5)
  ├── v0.1.4-multiinterface (Phase 3)
  ├── v0.1.5-hardening (Phase 4)
  ├── v0.1.7-agent-abstraction (Phase 6)
  ├── v0.1.8-standalone-web (Phase 7)
  └── v0.1.9-fhir-integration (Phase 8)

develop (integration branch)
  ├── feature/ekg-*
  ├── feature/langgraph-*
  ├── feature/mcp-server-*
  ├── feature/medsam2-*     ← 參考 MedRAX2
  ├── feature/agent-adapter-*   ← Agent 抽象層
  ├── feature/web-frontend-*    ← 獨立前端
  ├── feature/fhir-*            ← FHIR 整合
  ├── bugfix/*
  └── refactor/*
```

### Release Checklist
- [ ] All tests passing (coverage >= 85%)
- [ ] CHANGELOG updated with semantic version
- [ ] README updated with new features
- [ ] API documentation complete
- [ ] Example notebooks added (if applicable)
- [ ] Memory Bank updated (progress.md, architect.md)
- [ ] Git tag created (v0.X.Y)
- [ ] Release notes published

---

## Metrics & Success Indicators

### Phase Completion Metrics
| Phase | Primary Metric | Target | Status |
|-------|---|---|---|
| v0.1.1 | EKG model accuracy | >= 90% | ⏳ |
| v0.1.2 | Query routing accuracy | >= 95% | ⏳ |
| v0.1.3 | UI responsiveness | <= 2s | ⏳ |
| v0.1.4 | Interface coverage | 3/3 | ⏳ |
| v0.1.5 | Test coverage | >= 85% | ⏳ |
| v0.1.7 | Agent compatibility | >= 3 agents | ⏳ |
| v0.1.8 | Standalone deployment | Docker ready | ⏳ |
| v0.1.9 | FHIR compliance | SMART certified | ⏳ |

### User Metrics
- **Adoption**: GitHub stars, PyPI downloads, VS Code extension installs
- **Engagement**: Issue resolution time, community contributions
- **Quality**: Bug report frequency, user satisfaction surveys

---

## Risk & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|---|---|---|
| EKG model accuracy lower than expected | Medium | High | Start with benchmark datasets, use transfer learning |
| LangGraph learning curve | Low | Medium | Comprehensive documentation, example implementations |
| MCP spec changes | Low | High | Regular spec monitoring, version pinning |
| Copilot API stability | Medium | High | Multiple fallback mechanisms, graceful degradation |
| Resource constraints | High | High | Prioritize by impact, consider MVP approach |

---

## Contributing

Want to contribute to MedRAX Plus? See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

Follow our Constitutional Framework:
- 📜 Read [CONSTITUTION.md](CONSTITUTION.md) (highest principles)
- 📋 Check [.github/bylaws/](./github/bylaws/) (architectural rules)
- 🤖 Use [.claude/skills/](./claude/skills/) (automation tools)

---

## Questions or Feedback?

- 📧 Open an issue: [GitHub Issues](https://github.com/u9401066/MedRAX/issues)
- 💬 Join discussions: [GitHub Discussions](https://github.com/u9401066/MedRAX/discussions)
- 📖 See [ARCHITECTURE_MODERNIZATION.md](ARCHITECTURE_MODERNIZATION.md) for detailed design documents
