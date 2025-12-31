# MedRAX MCP Server 架構設計 (FastMCP + DDD)

> 雙層包裝設計：Copilot → MCP Server → MedRAX Backend → DL Models

## 1. 架構概述

### 當前問題分析

```
目前的簡單架構：
┌──────────────┐
│   Copilot    │
└────────┬─────┘
         │ Direct integration (複雜)
┌────────v──────────────────────┐
│   MedRAX Agent (LangChain)     │
│   ├─ CXR Tools                │
│   │  ├─ CheXagent             │
│   │  ├─ MedSAM                │
│   │  └─ LLaVA-Med             │
│   └─ EKG Tools                │
│      ├─ ResNet-ECG            │
│      └─ ECG-SQI               │
└────────────────────────────────┘
```

**問題**：
- ❌ Copilot 無法直接調用 MedRAX 複雜推理
- ❌ 無法利用 MCP 協議的優勢（模型上下文協議）
- ❌ 工具暴露不夠清晰

### 提議的雙層架構 ✅

```
多層次的抽象和職責分離

┌─────────────────────────────────────────────┐
│            Claude Copilot                    │
│  (User interface, task orchestration)        │
└──────────────────┬──────────────────────────┘
                   │ MCP Protocol
                   │ (JSON-RPC 2.0)
    ┌──────────────v────────────────────────────┐
    │     MedRAX MCP Server (FastMCP)            │
    │  ┌────────────────────────────────────┐   │
    │  │ Application Layer (MCP Handlers)   │   │
    │  │ ├─ analyze_cxr() tool             │   │
    │  │ ├─ analyze_ekg() tool             │   │
    │  │ └─ combined_analysis() tool       │   │
    │  └────────────────────────────────────┘   │
    │                 ↓                          │
    │  ┌────────────────────────────────────┐   │
    │  │ Domain Layer (Medical Reasoning)   │   │
    │  │ ├─ CXR Reasoning Service          │   │
    │  │ ├─ EKG Reasoning Service          │   │
    │  │ └─ Fusion Service                 │   │
    │  └────────────────────────────────────┘   │
    │                 ↓                          │
    │  ┌────────────────────────────────────┐   │
    │  │ Infrastructure Layer (Tool Wrapper)│   │
    │  │ ├─ CXR Tool Adapters              │   │
    │  │ │  ├─ CheXagent Wrapper           │   │
    │  │ │  ├─ MedSAM Wrapper              │   │
    │  │ │  └─ LLaVA-Med Wrapper           │   │
    │  │ └─ EKG Tool Adapters              │   │
    │  │    ├─ ResNet-ECG Wrapper          │   │
    │  │    └─ ECG-SQI Wrapper             │   │
    │  └────────────────────────────────────┘   │
    │                 ↓                          │
    │  ┌────────────────────────────────────┐   │
    │  │ Deep Learning Model Layer          │   │
    │  │ ├─ CXR Models (torch, tf)         │   │
    │  │ └─ EKG Models (torch, tf)         │   │
    │  └────────────────────────────────────┘   │
    └─────────────────────────────────────────────┘
```

### 優勢分析

| 方面 | 說明 |
|------|------|
| **抽象度** | ✅ 清晰的分層職責，易於測試和維護 |
| **可組合性** | ✅ MCP Tools 可被任何 MCP 客戶端重用（不只 Copilot） |
| **可擴展性** | ✅ 新增醫學工具只需在 Infrastructure 層添加 Wrapper |
| **解耦合** | ✅ Domain Logic 獨立於 MCP 協議實現 |
| **性能** | ⚠️ 多層轉包會增加開銷，但可優化 |

---

## 2. 雙層包裝的流程與考量

### 2.1 完整請求流程

```
Copilot Chat:
  User: "分析這個 X 光，告訴我右肺的異常"

  │ MCP Request (JSON-RPC 2.0)
  ├─ method: "tools/call"
  ├─ params: {
  │   "name": "analyze_cxr_region",
  │   "arguments": {
  │     "image_base64": "...",
  │     "region": {"type": "rect", "coords": [x1,y1,x2,y2]},
  │     "user_question": "右肺異常"
  │   }
  │ }
  │
  v MedRAX MCP Server
  
  MCP Handler: analyze_cxr_region()
  │ ┌─────────────────────────────┐
  │ │ Application Layer           │
  │ │ (Tool marshalling)          │
  │ └────────────┬────────────────┘
  │              │
  │              v
  │ ┌─────────────────────────────┐
  │ │ Domain: CXR Reasoning       │
  │ │ 1. Parse user intent        │
  │ │ 2. Route to sub-tools       │
  │ │ 3. Orchestrate calls        │
  │ │ 4. Fuse results             │
  │ └────────────┬────────────────┘
  │              │
  │              v
  │ ┌─────────────────────────────┐
  │ │ Infrastructure: Wrappers    │
  │ │ • Call CheXagent (region)   │
  │ │ • Call MedSAM (ROI extract) │
  │ │ • Call LLaVA-Med (VQA)      │
  │ └────────────┬────────────────┘
  │              │
  │              v
  │ ┌─────────────────────────────┐
  │ │ DL Models                   │
  │ │ • CUDA inference            │
  │ │ • Return embeddings/scores  │
  │ └────────────┬────────────────┘
  │              │
  │              v
  │ Result Fusion (Domain Layer)
  │ • Aggregate findings
  │ • Compute confidence
  │ • Format response
  │
  v
  
  MCP Response (JSON)
  {
    "type": "text",
    "text": "右肺發現：...",
    "confidence": 0.92
  }
  
  [ Optional: Include processed image ]
  {
    "type": "image",
    "base64": "...",  // With annotations
    "format": "png"
  }
  
  v Copilot displays results
```

### 2.2 性能考量

**開銷分析**：
```
Layer 1 (Copilot → MCP):
  • JSON 序列化/反序列化: ~10-50ms
  • 網絡延遲 (local): ~1-5ms
  • HTTP/WebSocket overhead: ~5-10ms
  小計: 20-65ms

Layer 2 (MCP → Domain):
  • Python 函數調用: <1ms
  • Domain orchestration: ~50-100ms
  • Tool selection: ~10-20ms
  小計: 60-120ms

Layer 3 (Infrastructure → Models):
  • Tool wrapper overhead: <5ms
  • GPU transfer: ~50-200ms (depends on model)
  • Inference: 100ms - 5s (depends on model)
  小計: 150ms - 5.2s

總計: 230ms - 5.4s (主要瓶頸在 DL 推理)
```

**優化策略**：
- ✅ 使用 MessagePack 而非 JSON（更快的序列化）
- ✅ 圖像分塊傳輸（避免超大 base64）
- ✅ 模型緩存和批處理
- ✅ 非同步 I/O

### 2.3 圖像流設計

**選項 A：簡潔模式（推薦首選）**
```
Response 中包含：
1. ✅ Text findings (結構化)
2. ✅ Confidence scores
3. ❌ 不返回處理圖（節省頻寬，Copilot UI 有限）

適用於：
- 快速反應優先
- 文本為主的分析
- Copilot 中展示有限空間
```

**選項 B：富媒體模式**
```
Response 中包含：
1. ✅ Text findings
2. ✅ Confidence scores
3. ✅ Annotated image (base64)
4. ✅ Heatmaps / 視覺化

適用於：
- 詳細分析模式
- 用戶需要視覺反饋
- 文檔和報告生成
```

**選項 C：流式模式（最優化）**
```
使用 SSE (Server-Sent Events) 或 WebSocket：

1. 流式返回部分結果
2. 漸進式加載
3. 圖像在最後返回（可選跳過）

適用於：
- 長時間處理
- 漸進式反饋重要
- 用戶可中斷
```

---

## 3. FastMCP + DDD Server 實現設計

### 3.1 項目結構

```
medrax-mcp-server/
├── mcp/
│   ├── __init__.py
│   ├── server.py              # FastMCP 伺服器進入點
│   └── handlers/
│       ├── __init__.py
│       ├── cxr_handler.py     # CXR 分析 Tool Handler
│       ├── ekg_handler.py     # EKG 分析 Tool Handler
│       └── fusion_handler.py  # 聯合分析 Tool Handler
│
├── application/
│   ├── __init__.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── cxr_service.py     # CXR 業務邏輯協調
│   │   ├── ekg_service.py     # EKG 業務邏輯協調
│   │   └── fusion_service.py  # 多模態融合
│   └── dtos/
│       ├── __init__.py
│       ├── cxr_dto.py         # CXR Request/Response DTO
│       ├── ekg_dto.py         # EKG Request/Response DTO
│       └── common_dto.py
│
├── domain/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── cxr_finding.py    # CXR 領域模型
│   │   ├── ekg_finding.py    # EKG 領域模型
│   │   └── clinical_assessment.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── cxr_analyzer.py   # 醫學推理服務
│   │   ├── ekg_analyzer.py
│   │   └── clinical_reasoner.py
│   └── exceptions.py
│
├── infrastructure/
│   ├── __init__.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── cxr/
│   │   │   ├── __init__.py
│   │   │   ├── chexagent_wrapper.py
│   │   │   ├── medsam_wrapper.py
│   │   │   └── llava_med_wrapper.py
│   │   └── ekg/
│   │       ├── __init__.py
│   │       ├── resnet_ecg_wrapper.py
│   │       ├── ecg_sqi_wrapper.py
│   │       └── pattern_matcher.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── image_repo.py      # DICOM/影像存儲
│   │   └── signal_repo.py     # ECG 信號存儲
│   └── config.py
│
├── utils/
│   ├── __init__.py
│   ├── image_processing.py    # 圖像預處理
│   ├── signal_processing.py   # 信號預處理
│   ├── cache.py               # 模型緩存
│   └── logging.py
│
├── tests/
│   ├── unit/
│   │   ├── test_cxr_service.py
│   │   ├── test_ekg_service.py
│   │   └── test_handlers.py
│   └── integration/
│       └── test_mcp_server.py
│
├── pyproject.toml
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
└── README.md
```

### 3.2 核心實現示例

#### FastMCP 伺服器骨架

```python
# mcp/server.py
from fastmcp import FastMCP
from mcp.handlers import cxr_handler, ekg_handler, fusion_handler

# 初始化 FastMCP 應用
app = FastMCP("medrax-medical-analyzer")

# 註冊 Tools
@app.tool()
async def analyze_cxr(
    image_base64: str,
    analysis_types: list[str] = ["segmentation", "classification"],
    region: dict | None = None,
) -> dict:
    """
    分析胸部 X 光影像
    
    Args:
        image_base64: Base64 編碼的影像
        analysis_types: 分析類型列表
        region: 感興趣的區域 {"type": "rect", "coords": [x1, y1, x2, y2]}
    
    Returns:
        {
            "findings": {...},
            "confidence": float,
            "image_annotated": str (optional base64)
        }
    """
    return await cxr_handler.handle_analyze_cxr(
        image_base64=image_base64,
        analysis_types=analysis_types,
        region=region,
    )

@app.tool()
async def analyze_ekg(
    signal_base64: str,
    signal_format: str = "csv",  # or "json", "binary"
    leads: int = 12,
) -> dict:
    """
    分析心電圖信號
    
    Args:
        signal_base64: 編碼的 EKG 信號
        signal_format: 信號格式
        leads: 導聯數 (通常 12)
    
    Returns:
        {
            "measurements": {...},
            "classifications": {...},
            "report": str,
            "confidence": float
        }
    """
    return await ekg_handler.handle_analyze_ekg(
        signal_base64=signal_base64,
        signal_format=signal_format,
        leads=leads,
    )

@app.tool()
async def combined_analysis(
    image_base64: str | None = None,
    signal_base64: str | None = None,
    clinical_context: dict | None = None,
) -> dict:
    """
    聯合 CXR 和 EKG 分析
    適用於心肺條件評估
    """
    return await fusion_handler.handle_combined_analysis(
        image_base64=image_base64,
        signal_base64=signal_base64,
        clinical_context=clinical_context,
    )
```

#### Application Layer - CXR 服務

```python
# application/services/cxr_service.py
from domain.services.cxr_analyzer import CXRAnalyzer
from infrastructure.tools.cxr import (
    CheXagentWrapper,
    MedSAMWrapper,
    LLavaMedWrapper,
)

class CXRAnalysisService:
    """
    CXR 分析協調服務
    職責：
    1. 解析用戶請求
    2. 協調多個基礎設施工具
    3. 呼叫領域分析器進行醫學推理
    4. 融合結果
    """
    
    def __init__(self):
        # 基礎設施層工具
        self.chexagent = CheXagentWrapper()
        self.medsam = MedSAMWrapper()
        self.llava_med = LLavaMedWrapper()
        
        # 領域層分析器
        self.analyzer = CXRAnalyzer()
    
    async def analyze(
        self,
        image_array: np.ndarray,
        analysis_types: list[str],
        region: dict | None = None,
    ) -> dict:
        """
        主要協調邏輯
        """
        findings = {}
        
        if "classification" in analysis_types:
            # 調用 CheXagent（使用 VQA）
            findings["pathology_scores"] = await self.chexagent.classify(
                image_array
            )
        
        if "segmentation" in analysis_types:
            # 調用 MedSAM（分割）
            findings["segmentation"] = await self.medsam.segment(
                image_array, region=region
            )
        
        if "grounding" in analysis_types:
            # 調用 LLaVA-Med（問答）
            findings["visual_qa"] = await self.llava_med.vqa(
                image_array,
                questions=["What are the main findings?", ...]
            )
        
        # 調用領域分析器進行醫學推理和融合
        clinical_assessment = await self.analyzer.reason(findings)
        
        return {
            "findings": clinical_assessment.to_dict(),
            "confidence": clinical_assessment.confidence,
            "reasoning_trace": clinical_assessment.trace,
        }
```

#### Domain Layer - 醫學分析器

```python
# domain/services/cxr_analyzer.py
from domain.models.cxr_finding import CXRFinding, Pathology
from domain.models.clinical_assessment import ClinicalAssessment

class CXRAnalyzer:
    """
    純醫學推理邏輯
    輸入：原始工具結果
    輸出：臨床評估
    """
    
    async def reason(self, findings: dict) -> ClinicalAssessment:
        """
        醫學推理主流程
        """
        assessment = ClinicalAssessment()
        
        # 1. 解析病理發現
        pathologies = self._parse_pathologies(
            findings.get("pathology_scores", {})
        )
        assessment.add_pathologies(pathologies)
        
        # 2. 定位分割結果
        if "segmentation" in findings:
            assessment.add_segmentation(findings["segmentation"])
        
        # 3. 整合視覺問答結果
        if "visual_qa" in findings:
            assessment.add_vqa_findings(findings["visual_qa"])
        
        # 4. 邏輯推理和置信度計算
        assessment.compute_confidence()
        
        # 5. 生成臨床報告
        assessment.generate_report()
        
        return assessment
    
    def _parse_pathologies(self, scores: dict) -> list[Pathology]:
        """
        將原始分數轉換為領域模型
        """
        pathologies = []
        for disease_name, score in scores.items():
            if score > 0.5:  # 置信度閾值
                pathologies.append(
                    Pathology(
                        name=disease_name,
                        confidence=score,
                        anatomical_location=self._infer_location(disease_name),
                    )
                )
        return pathologies
```

#### Infrastructure Layer - 工具包裝

```python
# infrastructure/tools/cxr/chexagent_wrapper.py
import torch
from torchvision import models, transforms

class CheXagentWrapper:
    """
    CheXagent 工具包裝
    職責：
    1. 模型加載和緩存
    2. 輸入預處理
    3. GPU 推理
    4. 結果後處理
    """
    
    def __init__(self, model_path: str = None):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self._load_model(model_path)
        self.transform = transforms.Compose([...])
    
    async def classify(self, image_array: np.ndarray) -> dict:
        """
        分類：返回 18 種病理的置信度
        """
        # 1. 預處理
        tensor = self.transform(image_array)
        
        # 2. 推理
        with torch.no_grad():
            logits = self.model(tensor.unsqueeze(0).to(self.device))
            probabilities = torch.softmax(logits, dim=1)
        
        # 3. 後處理
        results = {}
        pathology_names = [
            "Pneumonia", "Effusion", "Edema", 
            # ... 18 個病理
        ]
        for i, disease in enumerate(pathology_names):
            results[disease] = float(probabilities[0, i])
        
        return results
```

---

## 4. Copilot 集成流程

### 4.1 Copilot 使用流程

```typescript
// VS Code Extension (Copilot Participant)
// 用戶：@medrax 分析這個 X 光的右肺

vscode.chat.createChatParticipant('medrax', {
    invoke: async (request: vscode.ChatRequest, context, progress, token) => {
        // 1. 提取附件（圖像）
        const images = request.attachedImages;
        
        // 2. 構造 MCP 請求
        const mcpRequest = {
            jsonrpc: "2.0",
            id: uuid.v4(),
            method: "tools/call",
            params: {
                name: "analyze_cxr",
                arguments: {
                    image_base64: await encodeToBase64(images[0]),
                    analysis_types: ["classification", "segmentation"],
                    user_context: request.prompt,  // "右肺異常"
                }
            }
        };
        
        // 3. 調用 MCP Server
        const response = await mcpClient.call(mcpRequest);
        
        // 4. 解析響應
        const findings = response.result.findings;
        const confidence = response.result.confidence;
        
        // 5. 渲染到 Copilot
        const message = `
根據分析：
- 主要發現：${findings.primary_finding}
- 置信度：${confidence * 100}%
- 位置：${findings.anatomical_location}
- 建議：${findings.recommendations}
        `;
        
        return new vscode.LanguageModelChatMessage(
            vscode.LanguageModelChatMessageRole.Assistant,
            message
        );
    }
});
```

### 4.2 Copilot 聊天示例

```
User: @medrax 分析這個 X 光，我標記的區域看起來不尋常

[User 附加圖像 + 標記區域]

Copilot (MedRAX):
✓ 接收到 X 光影像
✓ 檢測到標記區域 (rect: 294,382 - 412,521)
✓ 執行分析...

結果：
主要發現：右下肺葉浸潤陰影，符合肺炎
置信度：92%
位置：右下肺葉，背側分段
臨床意義：急性感染，建議進一步影像和實驗室檢查

視覺化：
[顯示標註的 X 光影像，紅色框標記異常區域]

追蹤推理過程：
1. 分割模型確定了肺部邊界
2. 分類模型給出肺炎置信度 0.92
3. VQA 模型確認"浸潤陰影"特徵
4. 臨床推理層融合了所有結果
```

---

## 5. 圖像流決策

### 推薦方案：選項 A + B 混合

```python
# 響應結構
class MCPResponse:
    def __init__(self):
        # 必須返回
        self.findings_text = "..."  # 結構化文本
        self.confidence = 0.92
        self.measurements = {...}
        
        # 可選返回（基於請求或配置）
        self.include_visualizations = True
        
    def to_mcp_response(self):
        response = {
            "type": "text",
            "text": self.findings_text,
            "confidence": self.confidence,
        }
        
        # 如果請求端要求圖像，則包含
        if self.include_visualizations:
            response["_mcp_resource"] = {
                "uri": "file://annotated_image.png",
                "mimeType": "image/png",
                # 或 base64 編碼
                "base64": "...",
            }
        
        return response
```

### 決策矩陣

| 情景 | 返回圖像 | 理由 |
|------|---------|------|
| Copilot 快速查詢 | ❌ | 文本足夠，節省頻寬 |
| Copilot 詳細分析模式 | ✅ | 用戶要求視覺化 |
| 生成報告 | ✅ | 文檔需要圖像 |
| 移動/低頻寬 | ❌ | 優先考慮速度 |

---

## 6. 開發路線圖 (MCP Server)

### Phase 3.5 (v0.3.5): FastMCP 基礎框架
- [ ] 設置 FastMCP 伺服器骨架
- [ ] 實現 3 個基礎 Tools：analyze_cxr, analyze_ekg, combined_analysis
- [ ] 實現簡單的 Application Layer 協調
- [ ] Docker 容器化

**時間**: 2 weeks | **優先級**: 🔴 高

### Phase 3.6 (v0.3.6): DDD 完整實現
- [ ] 完整的 Domain Models (CXRFinding, EKGFinding, Clinical Assessment)
- [ ] Domain Services (CXRAnalyzer, EKGAnalyzer, ClinicalReasoner)
- [ ] 完整的 Infrastructure Layer (所有 Tool Wrapper)
- [ ] Repository Pattern for caching

**時間**: 2 weeks | **優先級**: 🔴 高

### Phase 3.7 (v0.3.7): VS Code Copilot 集成
- [ ] VS Code Extension 框架
- [ ] Copilot Participant 實現
- [ ] 圖像附件處理
- [ ] 區域標記支援

**時間**: 1-2 weeks | **優先級**: 🟡 中

### Phase 3.8 (v0.3.8): 優化和生產化
- [ ] 性能基準測試和優化
- [ ] 模型緩存策略
- [ ] 錯誤處理和重試機制
- [ ] 監控和日誌

**時間**: 1 week | **優先級**: 🟡 中

---

## 7. 成本-效益分析

### 為什麼使用雙層包裝？

| 因素 | 評分 | 說明 |
|------|------|------|
| **代碼重用** | ⭐⭐⭐⭐⭐ | Domain Logic 可被多個客戶端使用 |
| **標準化** | ⭐⭐⭐⭐⭐ | MCP 協議是行業標準 |
| **可維護性** | ⭐⭐⭐⭐⭐ | DDD 使代碼易於理解和修改 |
| **性能開銷** | ⭐⭐⭐ | 20-65ms 開銷可接受（主瓶頸在推理） |
| **實現複雜度** | ⭐⭐⭐ | 標準 FastMCP 模式，相對簡單 |

### 何時不使用雙層包裝

- ❌ 需要毫秒級延遲（低於 100ms）
- ❌ 團隊沒有 MCP 協議經驗
- ❌ 只會被 Copilot 使用（但為了未來擴展，還是建議用）

---

## 8. 實施檢查清單

### Before Starting Phase 3.5

- [ ] 確認 FastMCP 依賴版本
- [ ] 確認 DDD 層級分配
- [ ] 確認圖像流策略 (選擇 A/B/C)
- [ ] 確認 MCP 工具命名規範
- [ ] 準備測試 MCP 客戶端

### FastMCP Server Implementation

- [ ] 基礎伺服器架構
- [ ] 3 個初始 Tools 註冊
- [ ] Request/Response 序列化
- [ ] Error handling 框架
- [ ] 單元測試套件

### DDD 層實現

- [ ] Domain Models 定義
- [ ] Domain Services 邏輯
- [ ] Infrastructure Wrappers 實現
- [ ] DTOs 和映射
- [ ] 集成測試

### Copilot Integration

- [ ] VS Code 擴展骨架
- [ ] Copilot Participant 實現
- [ ] Image attachment 處理
- [ ] Region marking 解析
- [ ] E2E 測試

---

## 9. 圖像回傳策略 (關鍵問題解答)

### 9.1 圖像在整個流程中的生命週期

您的問題正確理解："用戶分成檔案傳 MedRAX, 文字問 GitHub Copilot，圖像回應在 MedRAX 上顯示 + MCP 回傳結果(圖像+文字)給 Copilot"

```
User uploads image
       ↓
[Stored in MedRAX backend]
  Original: /data/images/cxr_001.dcm
       ↓
[Copilot Chat]
"@medrax Analyze this CXR"
       ↓
MCP Server receives: image_id="cxr_001"
  (只是ID，不是實際圖像檔案)
       ↓
MedRAX Backend processes:
  1. Load: /data/images/cxr_001.dcm
  2. Run: CheXagent, MedSAM2, DenseNet
  3. Generate: /data/output/cxr_001_annotated.png
  4. Return: { findings, annotated_path, recommendations }
       ↓
MCP Server encodes image:
  base64_image = encode_to_base64(cxr_001_annotated.png)
       ↓
MCP Response to Copilot:
  {
    "findings": [...],
    "annotated_image": "iVBORw0KGgo...",  ← Base64 圖像
    "recommendations": [...]
  }
       ↓
Copilot displays:
  ![CXR](data:image/png;base64,iVBORw0KGgo...)
```

### 9.2 圖像回傳的三種方案

```python
# Option A: Base64 編碼（推薦用於 Copilot）
# 優點：完全獨立，無外部依賴；Copilot 可直接顯示
# 缺點：消息體較大

Response = {
  "findings": [...],
  "annotated_image": "data:image/png;base64,iVBORw0KGgo...",
  "image_format": "base64",
  "image_size_kb": 245
}

# Option B: 外部 URL（適合大型圖像）
Response = {
  "findings": [...],
  "annotated_image_url": "https://medrax-storage.example.com/cxr_001_annotated.png",
  "image_cache_ttl": 3600
}

# Option C: SVG 標註層（高級交互式）
Response = {
  "findings": [...],
  "image_layers": {
    "base": "data:image/png;base64,...",
    "annotations": [
      {"type": "bbox", "coords": [100, 200, 300, 400], "label": "pneumonia", "confidence": 0.92}
    ]
  }
}
```

### 9.3 推薦實現：Base64 + 壓縮

```python
from fastmcp import FastMCP
import base64
from PIL import Image
import io

app = FastMCP(name="medrax-mcp")

@app.tool()
async def analyze_cxr(image_id: str, focus_area: str = None) -> dict:
    """CXR 分析工具 - 返回 findings + annotated image (Base64)"""
    
    async with MedRAXClient() as client:
        # 1. 從 MedRAX 後端獲取分析結果
        result = await client.analyze_cxr(image_id=image_id, focus_area=focus_area)
        
        # 2. 讀取並壓縮標註後的圖像
        with open(result.annotated_image_path, 'rb') as f:
            image = Image.open(f)
            image.thumbnail((512, 512), Image.Resampling.LANCZOS)  # 可選壓縮
            
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            image_bytes = img_byte_arr.getvalue()
        
        # 3. 轉換為 Base64 (Copilot 可直接顯示)
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # 4. 返回 MCP 響應
        return {
            "status": "success",
            "findings": [{"type": f.type, "location": f.location, "confidence": f.confidence} 
                        for f in result.findings],
            "annotated_image": image_base64,  # ★ Copilot 可顯示
            "image_mime_type": "image/png",
            "clinical_report": result.report,
            "recommendations": result.recommendations,
        }
```

### 9.4 Copilot 中的顯示效果

```markdown
# CXR Analysis Result

## Findings
- Right lower lobe pneumonia - Confidence: 92%
- Air bronchogram present - Confidence: 88%

## Annotated Image
![CXR Annotation](data:image/png;base64,iVBORw0KGgo...)

## Clinical Report
The patient presents with a focal opacity in the right lower lobe...

## Recommendations
- Start antibiotic therapy
- Monitor O2 saturation
```

---

## 10. FAQ

| 問題 | 解答 |
|------|------|
| Base64 會使消息過大嗎？ | 壓縮至 512x512 後通常 < 500KB，可接受 |
| 多個圖像(CXR+EKG)如何處理？ | 返回多個 Base64 字段：`cxr_image`, `ekg_image` |
| 圖像隱私如何保證？ | 圖像只在 MedRAX 後端和用戶間傳輸，使用 TLS |

---

## 參考資源

- [MCP 規格](https://modelcontextprotocol.io/)
- [FastMCP 文檔](https://github.com/jlouis/fastmcp)
- [VS Code Extension API](https://code.visualstudio.com/api)
- [DDD in Python](https://verraes.net/2021/09/ddd-building-blocks-in-python/)

