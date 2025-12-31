# MedRAX 架構現代化方案

## 📊 1. 功能擴展：CXR + EKG 多模態醫學推理

### 當前狀況
- ✅ CXR（胸部 X 光）完整支援
- ✅ 13 個專業醫學工具
- ❌ 缺少心電圖（EKG/ECG）支援
- ❌ 多模態整合不完善

### 擴展方案

#### 1.1 EKG 分析工具棧
```
EKG Tools Layer:
├── Signal Processing
│   ├── ECG-SQI (信號品質評估)
│   ├── R-peak Detection
│   └── HRV Analysis (心率變異性)
├── ML Models
│   ├── ResNet-ECG (12-lead ECG classification)
│   ├── Transformer-ECG (異常檢測)
│   └── ArrhythmiaNet (心律不整分類)
└── Clinical Reasoning
    ├── ECG-BERT (臨床文本報告)
    ├── PatternMatcher (已知心律圖譜對比)
    └── RiskAssessment (風險評分)
```

#### 1.2 CXR + EKG 聯合推理
```python
# 例：肺炎患者同時有心律不整
CXR Finding: "Pneumonia in right lower lobe"
EKG Finding: "Atrial fibrillation with RVR"

Joint Reasoning:
- Sepsis risk assessment (考慮心律不整)
- Treatment interactions (肺炎藥物 × 心臟藥物)
- Monitoring priorities (優先監控心率 vs 氧飽和度)
```

---

## 🏗️ 2. Agent 架構現代化

### 當前架構分析
```
現狀：簡易線性流程
┌─────────────┐
│ User Query  │
└──────┬──────┘
       │
┌──────v──────┐
│LLM (思考)   │
└──────┬──────┘
       │
┌──────v──────────┐
│Tool Selection   │
└──────┬──────────┘
       │
┌──────v──────────┐
│Tool Execution   │
└──────┬──────────┘
       │
┌──────v──────────┐
│Return Result    │
└─────────────────┘
```

### 現代化方案：LangGraph + State Management

#### 2.1 多層架構
```
v0.3.0: LangGraph 重構

┌──────────────────────────────────────────────┐
│         Medical Reasoning Agent v0.3          │
├──────────────────────────────────────────────┤
│                                              │
│  ┌─────────────────────────────────────┐    │
│  │    Query Understanding & Routing     │    │
│  │  (Determine: CXR? EKG? Both?)       │    │
│  └────────────┬────────────────────────┘    │
│               │                              │
│       ┌───────┴────────┐                    │
│       │                │                    │
│  ┌────v────┐      ┌───v──────┐             │
│  │CXR Path │      │EKG Path  │             │
│  └────┬────┘      └───┬──────┘             │
│       │                │                    │
│  ┌────v────────────────v──────┐            │
│  │  Multi-Modal Fusion Layer   │            │
│  │ (聯合推理&相互驗證)         │            │
│  └────┬───────────────────────┘            │
│       │                                     │
│  ┌────v─────────────────────────────┐      │
│  │ Clinical Decision Support Layer   │      │
│  │ (風險評估、建議、解釋)            │      │
│  └────┬─────────────────────────────┘      │
│       │                                     │
│  ┌────v─────────────┐                      │
│  │  Response Format │                      │
│  │  (結構化輸出)     │                      │
│  └──────────────────┘                      │
│                                              │
└──────────────────────────────────────────────┘
```

#### 2.2 LangGraph 狀態機制
```python
# Agent State 設計
class MedicalReasoningState(TypedDict):
    """
    Medical multi-modal reasoning state
    """
    # 輸入
    query: str
    uploaded_images: List[Image]  # CXR、EKG 波形
    
    # 路由決策
    query_type: Literal["cxr", "ekg", "combined"]
    modalities_detected: List[str]
    
    # CXR 路徑
    cxr_findings: Dict[str, Any]  # 分割、分類、定位結果
    cxr_report: str
    
    # EKG 路徑
    ekg_signal: np.ndarray  # 原始信號
    ekg_features: Dict[str, float]  # HR, QT, ST segments 等
    ekg_classification: Dict[str, float]  # 各類心律分數
    ekg_report: str
    
    # 聯合層
    combined_context: str  # CXR + EKG 臨床背景
    
    # 決策支持
    clinical_decision: str
    risk_assessment: Dict[str, float]
    recommendations: List[str]
    
    # 解釋性
    reasoning_trace: List[str]  # 推理過程記錄
    
    # 輸出
    final_response: str
    confidence_scores: Dict[str, float]
```

#### 2.3 Tool Use Protocol (現代做法)
```python
# 新式 Tool Calling (Anthropic/OpenAI 標準)
class ToolUseNode:
    async def process(self, state: MedicalReasoningState):
        # LLM 決定用什麼工具
        response = await llm.apredict(
            system=system_prompt,
            messages=state.messages,
            tools=[
                # 工具以 JSON Schema 定義
                {
                    "name": "cxr_analysis",
                    "description": "分析胸部 X 光",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "image_id": {"type": "string"},
                            "analysis_types": {
                                "type": "array",
                                "items": {"enum": ["segmentation", "classification", "qa"]}
                            },
                            "user_marked_region": {
                                "type": "object",
                                "description": "使用者圈出的區域"
                            }
                        }
                    }
                },
                {
                    "name": "ekg_analysis",
                    "description": "分析心電圖",
                    "input_schema": {...}
                }
            ]
        )
        
        # 處理工具調用
        if response.tool_use:
            tool_result = await self.execute_tool(response.tool_use)
            # 更新狀態，繼續迴圈
        else:
            # LLM 已提供最終答案
            return response.text
```

---

## 🎨 3. UI/UX 現代化方案

### 3.1 實時標註與空間感知互動

#### 當前限制
```
現狀 (Gradio):
1️⃣ User: 上傳 X 光
2️⃣ Agent: 自動分析全圖
3️⃣ User: 閱讀報告
❌ 無法指定感興趣的區域
❌ 無法實時標註
❌ 互動有延遲
```

#### 改進方案 A: 增強版 Gradio UI
```python
# Gradio + Canvas 繪圖層
import gradio as gr
from gradio_canvas import Canvas

with gr.Blocks(theme=gr.themes.Soft()) as demo:
    with gr.Row():
        # 左: 影像 + 繪圖層
        with gr.Column():
            image_display = gr.Image(
                label="Medical Image",
                type="filepath"
            )
            # 使用者可在上面畫圈/方框
            annotation_canvas = Canvas(
                label="Mark regions of interest",
                value=None
            )
            
        # 右: 實時結果
        with gr.Column():
            findings_output = gr.Textbox(
                label="AI Findings",
                interactive=False,
                lines=20
            )
            confidence_chart = gr.BarChart(
                label="Confidence Scores",
                x="finding",
                y="confidence"
            )
    
    # 提交按鈕
    analyze_btn = gr.Button("Analyze Marked Regions", variant="primary")
    
    # 事件處理
    def analyze_with_context(image, annotations):
        """
        Args:
            image: PIL Image 或路徑
            annotations: {
                "regions": [
                    {"type": "rect", "coords": [x1, y1, x2, y2]},
                    {"type": "circle", "coords": [cx, cy, r]},
                ],
                "user_question": "What's this?"
            }
        """
        # 發送到 Agent 並加入空間上下文
        result = agent.analyze_with_focus(
            image=image,
            focused_regions=annotations["regions"],
            user_query=annotations.get("user_question", "")
        )
        return result.findings, result.confidence_scores
    
    analyze_btn.click(
        fn=analyze_with_context,
        inputs=[image_display, annotation_canvas],
        outputs=[findings_output, confidence_chart]
    )
```

### 3.2 多模態輸入與實時互動

```python
# 支持多種輸入方式
class MultiModalInterface:
    """
    支援：
    1. 影像標註 (Annotation)
    2. 語音輸入 (Voice)
    3. 文本查詢 (Text)
    4. 時間序列互動 (Temporal)
    """
    
    async def handle_user_interaction(self, 
                                     images: List[np.ndarray],
                                     annotations: Dict[str, Any],
                                     voice_input: Optional[bytes],
                                     text_query: str):
        """
        統一處理多模態輸入，構造豐富的上下文
        """
        
        context = {
            "visual": {
                "cxr": images[0] if images else None,
                "marked_regions": annotations,
                "user_attention": self._extract_saliency(annotations)
            },
            "linguistic": {
                "text_query": text_query,
                "voice_query": self._transcribe(voice_input),
                "intent": self._classify_intent(text_query)
            },
            "temporal": {
                "timestamp": datetime.now(),
                "session_id": self.session_id,
                "interaction_history": self.history[-5:]  # 最近5次互動
            }
        }
        
        # 發送到 Agent
        response = await self.agent.reason_multimodal(context)
        return response
```

### 3.3 Model 如何獲知用戶標註的區域

#### 方案 1: 區域嵌入 (Region Embedding)
```python
class RegionAwareAgent:
    """
    讓 LLM 理解用戶圈出的區域
    """
    
    async def process_marked_regions(self, 
                                    image: np.ndarray,
                                    marked_regions: List[Dict]):
        """
        標註 → 特徵提取 → LLM 提示詞
        """
        
        # Step 1: 為每個標記區域提取視覺特徵
        region_features = []
        for region in marked_regions:
            roi = self._extract_roi(image, region['coords'])
            
            # 使用 Vision Encoder 提取特徵
            features = self.vision_encoder.encode(roi)
            
            region_features.append({
                "id": region['id'],
                "location": self._describe_location(region['coords']),
                "visual_features": features,
                "user_question": region.get('question', '')
            })
        
        # Step 2: 構造增強提示詞
        system_prompt = f"""
        用戶在医学影像上標記了 {len(region_features)} 個感興趣區域。
        
        標記區域信息：
        {self._format_regions(region_features)}
        
        請針對這些標記區域進行深入分析。
        """
        
        # Step 3: 發送給 LLM
        response = await self.llm.apredict(
            messages=[
                SystemMessage(content=system_prompt),
                HumanMessage(content="Please analyze the marked regions"),
            ]
        )
        
        return response

    def _format_regions(self, regions: List[Dict]) -> str:
        """
        格式化區域信息給 LLM
        
        例：
        區域 1: 右下肺野 (294,382) - (412,521)
        用戶問題: "This looks abnormal?"
        視覺特徵: [0.23, 0.45, ..., 0.89]
        """
        formatted = []
        for i, region in enumerate(regions):
            desc = f"""
            區域 {i+1}: {region['location']}
            座標: {region['coords']}
            用戶疑問: {region.get('user_question', '無')}
            """
            formatted.append(desc)
        return "\n".join(formatted)
```

#### 方案 2: 視覺基礎模型 (Visual Foundation Model)
```python
class VisualGroundingAgent:
    """
    使用視覺基礎模型理解空間指代
    例: LLaVA-Grounding, Claude Vision, GPT-4V
    """
    
    async def ground_user_markup(self,
                                image: np.ndarray,
                                marked_regions: List[Dict],
                                user_query: str):
        """
        直接讓 LLM 看圖 + 標記
        """
        
        # Step 1: 在圖像上繪製用戶標記（視覺化）
        annotated_image = self._draw_annotations(image, marked_regions)
        
        # Step 2: 發送給多模態 LLM (GPT-4V, Claude 3.5)
        # 讓模型直接看到標記和原圖
        message = await self.vision_llm.apredict(
            images=[annotated_image],  # 標記已畫上去
            text=f"""
            用戶已在醫學影像上標記了 {len(marked_regions)} 個區域（紅色框）。
            
            用戶查詢: {user_query}
            
            請基於標記的區域進行詳細分析。
            """
        )
        
        return message
```

---

## 🤖 4. Agent 模式：Standalone vs MCP vs Copilot Integration

### 當前：Standalone Agent (v0.2)
```
User → Gradio UI → Agent → Tools → Response
```

### 選項 A: Model Context Protocol (MCP) Server
```
將 MedRAX 作為 MCP Server
┌────────────────────────────────┐
│    Claude / Any LLM Client      │
└────────────┬───────────────────┘
             │ MCP Protocol
┌────────────v───────────────────┐
│    MedRAX MCP Server            │
├────────────────────────────────┤
│ • cxr_analysis                  │
│ • ekg_analysis                  │
│ • clinical_decision_support     │
│ • image_grounding               │
│ • report_generation             │
└────────────────────────────────┘
```

**優點**：
- ✅ 由 Claude/GPT 控制推理流程
- ✅ 更靈活的多步推理
- ✅ 無限上下文歷史
- ✅ 更好的指令追蹤

**缺點**：
- ❌ 需要兼容客戶端
- ❌ 網絡延遲

### 選項 B: Copilot Integration (A2A 模式)
```
VS Code Copilot ←→ MedRAX Agent (via SDK)

在 VS Code 中直接使用 MedRAX:
User: @medrax analyze this CXR
                ↓
         Copilot Router
                ↓
         MedRAX Agent
                ↓
         Return results
         (inline in chat)
```

**需要實現**：
```typescript
// VS Code Extension (Copilot Participant)
vscode.chat.createChatParticipant('medrax', {
    invoke: async (request: vscode.ChatRequest) => {
        // 調用 MedRAX Agent
        const result = await medraxAgent.analyze({
            images: request.attachedImages,
            query: request.prompt
        });
        return result;
    }
});
```

**優點**：
- ✅ 無縫集成開發環境
- ✅ 訪問 Copilot 完整功能
- ✅ 支持代碼和文檔同時分析
- ✅ 本地執行（低延遲）

**缺點**：
- ❌ 限制在 VS Code 環境
- ❌ 需要 VS Code 擴展開發

### 選項 C: Hybrid (推薦) 🏆
```
v0.4.0: Unified Multi-Interface Agent

┌─────────────────────────────────────────┐
│          MedRAX Core Agent               │
│  (LangGraph + Multi-Modal Reasoning)     │
└──────────────────┬──────────────────────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
┌───v────┐   ┌────v─────┐   ┌───v────┐
│ Gradio │   │MCP Server│   │Copilot  │
│   UI   │   │          │   │Plugin   │
└────────┘   └──────────┘   └─────────┘

優點：
- 同時支持所有使用場景
- 用戶可選擇最適合的介面
- 共用同一個強大的 Agent 核心
```

---

## 📋 5. 實現路線圖

### Phase 1: 功能擴展 (v0.2.0) - 2025Q1
- [ ] EKG 信號處理工具
- [ ] ECG 分類模型集成
- [ ] CXR + EKG 聯合推理提示詞

### Phase 2: 架構現代化 (v0.3.0) - 2025Q1-Q2
- [ ] LangGraph 重構
- [ ] Tool Use Protocol 實現
- [ ] 狀態管理優化
- [ ] 多模態路由邏輯

### Phase 3: UI 互動增強 (v0.3.5) - 2025Q2
- [ ] 標註 Canvas 整合
- [ ] 區域感知推理
- [ ] 實時反饋改進

### Phase 4: Agent 模式 (v0.4.0) - 2025Q2-Q3
- [ ] MCP Server 實現
- [ ] VS Code Copilot 擴展
- [ ] Hybrid 界面管理

---

## 🛠️ 6. 技術深度

### 6.1 Region Awareness 實現細節

```python
class SpatialAwareAnalyzer:
    """
    理解用戶標記的區域位置和重要性
    """
    
    def analyze_with_spatial_context(self,
                                    image: np.ndarray,
                                    marked_regions: List[Bbox],
                                    anatomical_context: Dict):
        """
        例：用戶圈出右下肺野
        
        系統回應應該：
        1. 說明找到的異常位置
        2. 與已知解剖特徵比較
        3. 提供定位信息 (using anatomical landmarks)
        4. 評估臨床意義
        """
        
        # 1. 解剖定位
        for region in marked_regions:
            anatomical_location = self.anatomical_localizer(
                region.bbox,
                anatomical_context
            )
            print(f"用戶標記位置: {anatomical_location}")
            # e.g., "Right lower lobe, lateral segment"
        
        # 2. 檢索相似病例
        similar_cases = self.case_retriever.find_similar(
            marked_regions=marked_regions,
            query_image=image
        )
        
        # 3. 生成定位化報告
        report = self.report_generator.generate(
            findings=findings,
            spatial_context=marked_regions,
            similar_cases=similar_cases
        )
        
        return report
```

### 6.2 EKG 信號處理流程

```python
class ECGAnalyzer:
    """
    12-lead ECG 完整分析
    """
    
    async def full_analysis(self, ecg_signal: np.ndarray):
        """
        Input: (12, 5000) - 12 leads, 5000 samples
        """
        
        # 1. 信號品質評估
        quality = self.assess_signal_quality(ecg_signal)
        
        # 2. 特徵提取
        features = {
            "heart_rate": self.calculate_heart_rate(ecg_signal),
            "pr_interval": self.measure_pr(ecg_signal),
            "qrs_duration": self.measure_qrs(ecg_signal),
            "qt_interval": self.measure_qt(ecg_signal),
            "st_segment": self.analyze_st(ecg_signal),
            "t_wave": self.analyze_t_wave(ecg_signal),
        }
        
        # 3. 深度學習分類
        classifications = await self.ecg_classifier(ecg_signal)
        # Output: {
        #   "normal": 0.92,
        #   "atrial_fibrillation": 0.05,
        #   "left_ventricular_hypertrophy": 0.02,
        #   ...
        # }
        
        # 4. 臨床推理
        clinical_report = self.reasoning_engine.generate_report(
            features=features,
            classifications=classifications,
            quality=quality
        )
        
        return {
            "features": features,
            "classifications": classifications,
            "clinical_report": clinical_report,
            "quality_score": quality
        }
```

---

## 📊 總結與建議

| 維度 | 現狀 | 目標 (v0.4) | 優先級 |
|------|------|----------|--------|
| **功能** | CXR only | CXR + EKG | 🔴 高 |
| **Agent** | 簡易線性 | LangGraph + MCP | 🔴 高 |
| **UI** | 靜態上傳 | 動態標註 + 多模態 | 🟡 中 |
| **集成** | Gradio 獨立 | Hybrid (Gradio+MCP+Copilot) | 🟡 中 |

**建議順序**：
1. ✅ v0.2.0: EKG 工具 + 聯合推理 (2 weeks)
2. ✅ v0.3.0: LangGraph 重構 (3 weeks)
3. ✅ v0.3.5: 標註 Canvas (1 week)
4. ✅ v0.4.0: MCP + Copilot (4 weeks)

