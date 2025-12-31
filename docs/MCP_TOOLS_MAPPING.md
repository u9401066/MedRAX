# MedRAX Tools → MCP Tools 映射設計

> 分析現有 LangChain Tools 並設計對應的 FastMCP Tools

---

## 🔄 關鍵：資料流邏輯對比

### 原 MedRAX 資料流（LangGraph + LLM 整合）

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        原 MedRAX 架構                                    │
└─────────────────────────────────────────────────────────────────────────┘

User Query + Image
       │
       ▼
┌──────────────────┐
│  Gradio UI       │  ← interface.py
│  - 上傳圖像       │
│  - Base64 編碼   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  GPT-4o (LLM)    │  ← main.py: ChatOpenAI(model="gpt-4o")
│  + System Prompt │  ← "You are an expert medical AI assistant..."
│  + bind_tools()  │  ← 綁定所有工具
└────────┬─────────┘
         │
         │ LLM 決定調用哪些工具
         ▼
┌──────────────────┐
│  Agent.execute_  │  ← agent.py: execute_tools()
│  tools()         │
│  - 執行工具      │
│  - 返回 ToolMsg  │
└────────┬─────────┘
         │
         │ Tool Results (Dict + Metadata)
         ▼
┌──────────────────┐
│  GPT-4o 再次     │  ← ★關鍵：LLM 整合結果！
│  處理工具輸出     │
│  - 解釋報告      │
│  - 綜合分析      │
│  - 臨床建議      │
└────────┬─────────┘
         │
         │ Final Response
         ▼
┌──────────────────┐
│  Gradio UI       │  ← 顯示最終回應
│  - 文字回應      │
│  - 圖像（如有）   │
└──────────────────┘

關鍵循環（agent.py）：
process_request() → has_tool_calls? → execute_tools() → process_request() → END
     ↑                                      │
     └──────────────────────────────────────┘
     (LLM 看到工具結果後，再生成最終回應)
```

### 新 MCP 架構資料流（Copilot 為 Agent）

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        MCP 架構 (MedRAX Plus)                           │
└─────────────────────────────────────────────────────────────────────────┘

User Query (Text)              User Image Upload
       │                              │
       ▼                              ▼
┌──────────────────┐          ┌──────────────────┐
│  VS Code Copilot │          │  MedRAX Backend  │
│  Chat Window     │          │  (Gradio/API)    │
│  @medrax ...     │          │  - 存儲圖像       │
└────────┬─────────┘          │  - 返回 image_id │
         │                    └────────┬─────────┘
         │                             │
         │ MCP Protocol                │ image_id
         ▼                             │
┌──────────────────┐                   │
│  GitHub Copilot  │  ← Claude/GPT-4o  │
│  (Agent 角色)    │                   │
│  - 理解意圖      │                   │
│  - 規劃工具調用   │                   │
└────────┬─────────┘                   │
         │                             │
         │ Tool Call Request           │
         ▼                             │
┌──────────────────────────────────────┴──────────┐
│  MedRAX MCP Server (FastMCP)                    │
│  ┌────────────────────────────────────────────┐ │
│  │ @app.tool() classify_cxr(image_id)         │ │
│  │ @app.tool() ask_cxr_expert(image_id, q)    │ │
│  │ @app.tool() segment_anatomy(image_id)      │ │
│  └────────────────────────────────────────────┘ │
│       │                                         │
│       │ 調用 Infrastructure Layer               │
│       ▼                                         │
│  ┌────────────────────────────────────────────┐ │
│  │ ChestXRayClassifierWrapper (DenseNet-121)  │ │
│  │ XRayVQAWrapper (CheXagent)                 │ │
│  │ SegmentationWrapper (PSPNet)               │ │
│  └────────────────────────────────────────────┘ │
│       │                                         │
│       │ 結構化結果 + Base64 圖像                 │
│       ▼                                         │
│  Return: { findings, annotated_image, ... }     │
└─────────────────────────┬───────────────────────┘
                          │
                          │ MCP Response
                          ▼
┌──────────────────────────────────────────────────┐
│  GitHub Copilot (Agent)                          │
│  ★★★ 關鍵：Copilot 負責整合結果！★★★           │
│                                                  │
│  Copilot 接收到工具結果後：                       │
│  1. 解讀 findings 數據                           │
│  2. 理解 confidence scores                       │
│  3. 綜合多個工具結果                             │
│  4. 生成臨床解釋和建議                           │
│  5. 格式化為用戶友好的 Markdown                  │
└─────────────────────────┬────────────────────────┘
                          │
                          │ Final Response
                          ▼
┌──────────────────────────────────────────────────┐
│  VS Code Copilot Chat                            │
│  ## CXR Analysis Results                         │
│  ### Findings                                    │
│  - Pneumonia (Right lower lobe) - 92%           │
│  ### Annotated Image                             │
│  ![CXR](data:image/png;base64,...)              │
│  ### Clinical Interpretation                    │
│  Based on the findings, this patient...         │
└──────────────────────────────────────────────────┘
```

### ⚠️ 關鍵差異與解決方案

| 方面 | 原 MedRAX | MCP 架構 | 解決方案 |
|------|----------|----------|----------|
| **LLM 整合** | GPT-4o 在 agent.py 循環整合 | Copilot 整合 | ✅ Copilot 本身就是 LLM |
| **System Prompt** | 自定義 medical prompt | Copilot 預設 | ⚠️ MCP Prompt 補充醫學指引 |
| **多輪工具調用** | LangGraph 循環 | Copilot 決定 | ✅ Copilot 可多次調用 |
| **圖像傳遞** | image_path 本地 | image_id 引用 | ✅ Base64 返回 |
| **臨床推理** | LLM 最後一步 | Copilot 最後一步 | ✅ 職責相同 |

### 🔧 MCP Prompt 補充（確保臨床推理品質）

```python
@app.prompt("clinical_reasoning")
def clinical_reasoning_prompt() -> str:
    """提供給 Copilot 的醫學推理指引"""
    return """
    When analyzing medical images using MedRAX tools:
    
    1. INTERPRET tool results in clinical context
       - Explain clinical significance, not just numbers
       - Compare against normal ranges
    
    2. INTEGRATE multiple tool outputs
       - Correlate classification + segmentation + grounding
       - Cross-reference findings
    
    3. PROVIDE clinical recommendations
       - Severity assessment
       - Suggested follow-up
       - Differential diagnoses
    
    4. ACKNOWLEDGE limitations
       - AI is supportive, not diagnostic
       - Recommend clinical correlation
    
    5. FORMAT for clinical readability
       - Structured sections (Findings, Impression, Recommendations)
       - Show annotated images
    """
```

### ✅ 資料流驗證清單

- [x] 圖像上傳：用戶 → MedRAX Backend → image_id
- [x] 查詢處理：用戶 → Copilot → 理解意圖
- [x] 工具調用：Copilot → MCP Server → Tool Wrapper → DL Model
- [x] 結果返回：Tool → MCP Server → Copilot (JSON + Base64)
- [x] **結果整合：Copilot (LLM) 解讀並生成臨床解釋** ← 關鍵！
- [x] 最終顯示：Copilot → VS Code Chat (Markdown + 圖像)

---

## 現有工具清單

| 檔案 | LangChain Tool Class | 功能 | 優先級 |
|------|---------------------|------|--------|
| `classification.py` | `ChestXRayClassifierTool` | 18 種病理分類 (DenseNet-121) | 🔴 高 |
| `xray_vqa.py` | `XRayVQATool` | CheXagent VQA | 🔴 高 |
| `segmentation.py` | `ChestXRaySegmentationTool` | 14 種器官分割 (PSPNet) | 🔴 高 |
| `grounding.py` | `XRayPhraseGroundingTool` | 病灶定位 (Maira-2) | 🟡 中 |
| `report_generation.py` | `ChestXRayReportGeneratorTool` | 報告生成 (ViT-BERT) | 🟡 中 |
| `llava_med.py` | `LlavaMedTool` | 通用醫學 VQA | 🟡 中 |
| `generation.py` | `ChestXRayGeneratorTool` | X光合成 (RoentGen) | 🟢 低 |
| `dicom.py` | `DicomProcessorTool` | DICOM 處理 | 🔴 高 |
| `utils.py` | `ImageVisualizerTool` | 圖像顯示 | 🟢 低 |

---

## 1. MCP Tools 設計原則

### 1.1 LangChain → FastMCP 轉換模式

```python
# LangChain Tool 結構
class SomeTool(BaseTool):
    name: str = "tool_name"
    description: str = "..."
    args_schema: Type[BaseModel] = SomeInput
    
    def _run(self, **args) -> Tuple[Dict, Dict]:
        ...

# 對應的 FastMCP Tool
from fastmcp import FastMCP

app = FastMCP("medrax-mcp")

@app.tool()
async def tool_name(
    param1: str,
    param2: Optional[int] = None
) -> dict:
    """Tool description (用於 MCP schema)"""
    # 調用原始 LangChain Tool 或重新實現
    ...
```

### 1.2 圖像處理策略

```python
# 輸入：image_id (而非 image_path)
# MedRAX 後端管理圖像存儲

@app.tool()
async def analyze_cxr(image_id: str, ...) -> dict:
    # 1. 從 MedRAX 後端獲取圖像路徑
    image_path = await backend.get_image_path(image_id)
    
    # 2. 執行分析
    result = tool.invoke({"image_path": image_path})
    
    # 3. 處理輸出圖像（如有）
    if result.get("output_image_path"):
        # 轉為 Base64 或 URL
        output_image = encode_image(result["output_image_path"])
    
    # 4. 返回結構化結果
    return {
        "findings": [...],
        "annotated_image": output_image,  # Base64
        ...
    }
```

---

## 2. 高優先級 Tools (v0.1.4-alpha)

### 2.1 `classify_cxr` - 病理分類

**來源**: `ChestXRayClassifierTool`

```python
@app.tool()
async def classify_cxr(
    image_id: str,
    pathologies: Optional[List[str]] = None,  # 篩選特定病理
    threshold: float = 0.5  # 信心分數閾值
) -> dict:
    """
    對胸部 X 光進行 18 種病理分類。
    
    病理包括：Atelectasis, Cardiomegaly, Consolidation, Edema, 
    Effusion, Emphysema, Enlarged Cardiomediastinum, Fibrosis, 
    Fracture, Hernia, Infiltration, Lung Lesion, Lung Opacity, 
    Mass, Nodule, Pleural Thickening, Pneumonia, Pneumothorax
    
    Args:
        image_id: 已上傳圖像的 ID
        pathologies: 只返回指定病理（可選）
        threshold: 信心分數閾值，低於此值不返回
    
    Returns:
        dict: 包含 classifications (病理及分數) 和 metadata
    """
    ...
```

**MCP JSON Schema**:
```json
{
  "name": "classify_cxr",
  "description": "對胸部 X 光進行 18 種病理分類",
  "inputSchema": {
    "type": "object",
    "properties": {
      "image_id": {"type": "string", "description": "已上傳圖像的 ID"},
      "pathologies": {
        "type": "array",
        "items": {"type": "string"},
        "description": "篩選特定病理"
      },
      "threshold": {"type": "number", "default": 0.5}
    },
    "required": ["image_id"]
  }
}
```

---

### 2.2 `ask_cxr_expert` - 視覺問答

**來源**: `XRayVQATool` (CheXagent)

```python
@app.tool()
async def ask_cxr_expert(
    image_ids: List[str],
    question: str,
    max_tokens: int = 512
) -> dict:
    """
    使用 CheXagent 對胸部 X 光進行視覺問答。
    
    支援任務：
    - 視覺問答（"這張 X 光有什麼發現？"）
    - 報告生成（"生成放射科報告"）
    - 異常檢測（"有沒有肺炎的跡象？"）
    - 比較分析（"這兩張 X 光有什麼變化？"）
    
    Args:
        image_ids: 圖像 ID 列表（支援多張比較）
        question: 自然語言問題
        max_tokens: 最大回應長度
    
    Returns:
        dict: 包含 answer, confidence, reasoning
    """
    ...
```

---

### 2.3 `segment_anatomy` - 解剖分割

**來源**: `ChestXRaySegmentationTool`

```python
@app.tool()
async def segment_anatomy(
    image_id: str,
    organs: Optional[List[str]] = None,
    return_metrics: bool = True,
    return_visualization: bool = True
) -> dict:
    """
    對胸部 X 光進行解剖結構分割。
    
    可分割器官（14 種）：
    - 骨骼：Left/Right Clavicle, Left/Right Scapula, Spine
    - 肺部：Left/Right Lung, Left/Right Hilus Pulmonis
    - 心血管：Heart, Aorta, Mediastinum
    - 其他：Facies Diaphragmatica, Weasand
    
    Args:
        image_id: 已上傳圖像的 ID
        organs: 只分割指定器官（可選，默認全部）
        return_metrics: 返回面積、位置等測量數據
        return_visualization: 返回分割可視化圖像
    
    Returns:
        dict: 包含 segmentation_masks, metrics, visualization_image
    """
    ...
```

---

### 2.4 `process_dicom` - DICOM 處理

**來源**: `DicomProcessorTool`

```python
@app.tool()
async def process_dicom(
    dicom_id: str,
    window_center: Optional[float] = None,
    window_width: Optional[float] = None
) -> dict:
    """
    處理 DICOM 文件並轉換為標準圖像格式。
    
    自動應用窗位窗寬調整，提取元數據。
    
    Args:
        dicom_id: 已上傳 DICOM 文件的 ID
        window_center: 窗位（可選，使用 DICOM 預設）
        window_width: 窗寬（可選，使用 DICOM 預設）
    
    Returns:
        dict: 包含 processed_image_id, metadata (PatientID, StudyDate, etc.)
    """
    ...
```

---

## 3. 中優先級 Tools (v0.1.4-beta)

### 3.1 `ground_finding` - 病灶定位

**來源**: `XRayPhraseGroundingTool` (Maira-2)

```python
@app.tool()
async def ground_finding(
    image_id: str,
    finding: str,
    return_visualization: bool = True
) -> dict:
    """
    在胸部 X 光中定位特定醫學發現。
    
    Args:
        image_id: 已上傳圖像的 ID
        finding: 要定位的醫學發現（如 "Pleural effusion", "Cardiomegaly"）
        return_visualization: 返回標註後的圖像
    
    Returns:
        dict: 包含 bounding_boxes (0-1 相對座標), visualization_image
    """
    ...
```

### 3.2 `generate_report` - 報告生成

**來源**: `ChestXRayReportGeneratorTool`

```python
@app.tool()
async def generate_report(
    image_id: str,
    sections: List[str] = ["findings", "impression"]
) -> dict:
    """
    為胸部 X 光生成放射科報告。
    
    Args:
        image_id: 已上傳圖像的 ID
        sections: 要生成的報告章節
    
    Returns:
        dict: 包含 findings_text, impression_text, full_report
    """
    ...
```

### 3.3 `ask_medical_expert` - 通用醫學 VQA

**來源**: `LlavaMedTool`

```python
@app.tool()
async def ask_medical_expert(
    question: str,
    image_id: Optional[str] = None
) -> dict:
    """
    使用 LLaVA-Med 回答通用醫學問題。
    
    注意：對於胸部 X 光專門分析，建議使用 ask_cxr_expert。
    
    Args:
        question: 醫學問題
        image_id: 相關圖像（可選）
    
    Returns:
        dict: 包含 answer, confidence
    """
    ...
```

---

## 4. 低優先級 Tools (v0.1.4+)

### 4.1 `generate_synthetic_xray` - X光合成

**來源**: `ChestXRayGeneratorTool`

```python
@app.tool()
async def generate_synthetic_xray(
    description: str,
    size: Tuple[int, int] = (512, 512)
) -> dict:
    """
    根據文字描述生成合成胸部 X 光。
    
    注意：僅供教學和研究用途，不可用於臨床診斷。
    
    Args:
        description: 醫學狀況描述（如 "large left-sided pleural effusion"）
        size: 圖像尺寸
    
    Returns:
        dict: 包含 generated_image_id, generation_metadata
    """
    ...
```

---

## 5. 複合 Tools (高階功能)

### 5.1 `comprehensive_cxr_analysis` - 綜合分析

```python
@app.tool()
async def comprehensive_cxr_analysis(
    image_id: str,
    include_classification: bool = True,
    include_segmentation: bool = True,
    include_report: bool = True,
    clinical_context: Optional[str] = None
) -> dict:
    """
    對胸部 X 光進行全面分析，整合多個工具結果。
    
    流程：
    1. 病理分類（18 類）
    2. 解剖分割（14 器官）
    3. 報告生成（發現 + 印象）
    4. 臨床推理（整合所有結果）
    
    Args:
        image_id: 已上傳圖像的 ID
        include_classification: 包含病理分類
        include_segmentation: 包含解剖分割
        include_report: 包含報告生成
        clinical_context: 臨床背景（如 "62歲男性，咳嗽2週"）
    
    Returns:
        dict: 綜合分析結果
    """
    ...
```

### 5.2 `compare_cxr_studies` - 比較分析

```python
@app.tool()
async def compare_cxr_studies(
    current_image_id: str,
    prior_image_id: str,
    focus_areas: Optional[List[str]] = None
) -> dict:
    """
    比較兩張胸部 X 光（當前 vs 先前）。
    
    Args:
        current_image_id: 當前圖像 ID
        prior_image_id: 先前圖像 ID
        focus_areas: 重點關注區域（如 ["lung", "heart"]）
    
    Returns:
        dict: 包含 changes_detected, progression_assessment, comparison_image
    """
    ...
```

---

## 6. MCP Resources 設計

```python
@app.resource("medrax://images/{image_id}")
async def get_image_resource(image_id: str) -> Resource:
    """獲取圖像資訊和縮略圖"""
    return Resource(
        uri=f"medrax://images/{image_id}",
        name=f"CXR Image {image_id}",
        mimeType="image/png",
        description="Chest X-ray image"
    )

@app.resource("medrax://pathologies")
async def get_pathology_list() -> Resource:
    """獲取支援的病理列表"""
    return Resource(
        uri="medrax://pathologies",
        name="Supported Pathologies",
        mimeType="application/json",
        text=json.dumps(PATHOLOGY_LIST)
    )

@app.resource("medrax://organs")
async def get_organ_list() -> Resource:
    """獲取支援的器官分割列表"""
    return Resource(
        uri="medrax://organs",
        name="Segmentable Organs",
        mimeType="application/json",
        text=json.dumps(ORGAN_LIST)
    )
```

---

## 7. DDD 架構映射

```
┌─────────────────────────────────────────────────────────────┐
│ Presentation Layer (MCP Tools)                               │
│ ├── classify_cxr()                                          │
│ ├── ask_cxr_expert()                                        │
│ ├── segment_anatomy()                                       │
│ └── ...                                                     │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│ Application Layer (Services)                                 │
│ ├── ClassificationService                                   │
│ ├── VQAService                                              │
│ ├── SegmentationService                                     │
│ └── ReportService                                           │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│ Domain Layer (Models & Logic)                                │
│ ├── CXRFinding (病理發現)                                    │
│ ├── SegmentationResult (分割結果)                            │
│ ├── ClinicalAssessment (臨床評估)                            │
│ └── MedicalReasoningService (推理邏輯)                       │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│ Infrastructure Layer (Tool Wrappers)                         │
│ ├── ChestXRayClassifierWrapper  ← classification.py         │
│ ├── XRayVQAWrapper              ← xray_vqa.py              │
│ ├── SegmentationWrapper         ← segmentation.py          │
│ ├── GroundingWrapper            ← grounding.py             │
│ ├── ReportGeneratorWrapper      ← report_generation.py     │
│ ├── LlavaMedWrapper             ← llava_med.py             │
│ ├── DicomProcessorWrapper       ← dicom.py                 │
│ └── XRayGeneratorWrapper        ← generation.py            │
└─────────────────────────────────────────────────────────────┘
```

---

## 8. 實現優先順序

### Phase v0.1.4-alpha（2 週）
1. ✅ 設置 FastMCP 基礎框架
2. ✅ 實現 `classify_cxr`
3. ✅ 實現 `ask_cxr_expert`
4. ✅ 實現 `process_dicom`
5. ✅ 基本圖像處理（Base64 編碼）

### Phase v0.1.4-beta（2 週）
1. ✅ 實現 `segment_anatomy`
2. ✅ 實現 `ground_finding`
3. ✅ 實現 `generate_report`
4. ✅ DDD 分層重構
5. ✅ Infrastructure Wrappers

### Phase v0.1.4-rc（1-2 週）
1. ✅ 實現 `comprehensive_cxr_analysis`
2. ✅ 實現 `compare_cxr_studies`
3. ✅ MCP Resources
4. ✅ Copilot 整合測試

---

## 9. vs MedRAX2 對比

| 功能 | MedRAX (現有) | MedRAX2 (新增) | MedRAX Plus MCP |
|------|--------------|----------------|-----------------|
| 分類 | DenseNet-121 | + ArcPlus | 兩者都支援 |
| VQA | CheXagent | + MedGemma | 優先 CheXagent |
| 分割 | PSPNet | + MedSAM2 | 優先 MedSAM2 |
| 定位 | Maira-2 | 同 | 同 |
| 報告 | ViT-BERT | 同 | 同 |
| 通用 VQA | LLaVA-Med | 同 | 同 |
| 合成 | RoentGen | 同 | 同 |
| Python 沙盒 | ❌ | ✅ | ⚠️ 透過 MCP 處理 |
| 網頁搜尋 | ❌ | ✅ | ⚠️ 低優先 |
| RAG | ❌ | ✅ | 🔜 v0.1.5+ |

**我們的優勢**：
- MCP 協議標準化
- DDD 架構清晰
- Copilot 原生整合
- EKG 多模態（規劃中）
