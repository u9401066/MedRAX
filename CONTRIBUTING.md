# 貢獻指南

感謝你有興趣為 MedRAX 做出貢獻！

## 如何貢獻

### 回報問題 (Bug Report)

1. 先搜尋現有 Issues，確認問題未被回報
2. 使用 [Bug Report 模板](.github/ISSUE_TEMPLATE/bug_report.md) 提交問題
3. 提供清晰的重現步驟：
   - 使用的醫學工具版本
   - 輸入影像類型 (DICOM format, 解析度等)
   - 預期行為 vs 實際行為
   - 完整的錯誤訊息

### 功能建議 (Feature Request)

1. 先搜尋現有 Issues
2. 使用 [Feature Request 模板](.github/ISSUE_TEMPLATE/feature_request.md)
3. 描述醫學應用場景：
   - 支援的診斷任務
   - 整合新醫學工具的必要性
   - 預期使用者（臨床醫生、研究者等）

### 提交程式碼 (Pull Request)

#### 1. 環境設定

```bash
# 複製專案
git clone https://github.com/u9401066/MedRAX.git
cd MedRAX

# 建立虛擬環境（使用 uv）
uv venv
source .venv/bin/activate  # Linux/macOS
# 或 .venv\Scripts\activate  # Windows

# 安裝開發依賴
uv pip install -e ".[dev,test]"

# 啟用 pre-commit hooks
pre-commit install
```

#### 2. 代碼規範

遵循以下規範：

**風格檢查**
```bash
# 代碼格式化
black medrax/

# Import 排序
isort medrax/

# Lint 檢查
ruff check medrax/

# 靜態分析
mypy medrax/
```

**DDD 架構遵循**
- Domain Logic: 純醫學推理，無外部依賴
- Infrastructure: 所有工具調用必須在此層
- Services: 通過 Repository Pattern 訪問資源

#### 3. 提交流程

```bash
# 1. 更新記憶庫
#    編輯 memory-bank/activeContext.md (當前工作)
#    編輯 memory-bank/progress.md (完成任務)

# 2. 創建 Feature Branch
git checkout -b feat/your-feature-name

# 3. 提交變更
git add .
git commit -m "feat: 新增 XXX 工具支援"

# 4. 推送並建立 PR
git push origin feat/your-feature-name
```

**Commit Message 規範**
```
<type>(<scope>): <subject>

<body>

<footer>
```

類型 (type):
- `feat`: 新功能（新醫學工具、新推理能力）
- `fix`: 錯誤修復（工具調用錯誤、推理邏輯缺陷）
- `refactor`: 代碼重構（架構優化、工具隔離）
- `test`: 測試相關（新增測試、測試覆蓋率）
- `docs`: 文檔更新（README、API 文檔）
- `perf`: 性能優化（推理加速、記憶優化）

範圍 (scope):
- `agent`: 代理編排邏輯
- `tools`: 醫學工具集成
- `dicom`: DICOM 處理模組
- `ui`: Gradio 介面
- `docs`: 文檔系統
- `memory`: 記憶庫系統

主題 (subject):
- 使用命令式語氣（"add" not "added"）
- 不要大寫首字母
- 不要以句號結尾
- 限制在 50 個字元

#### 4. 測試要求

所有新功能必須包含測試：

```bash
# 運行所有測試
pytest

# 檢查覆蓋率（目標 80%+）
pytest --cov=medrax

# 運行特定測試
pytest tests/test_tools/test_chexagent.py
```

**測試位置**: `tests/`

**測試命名規範**:
- Unit tests: `test_<module_name>.py`
- Integration tests: `test_<feature_name>_integration.py`

### 5. Pull Request 檢查清單

提交 PR 前請確保：

- [ ] 遵循代碼風格規範 (`black`, `isort`, `ruff`)
- [ ] 所有新功能都有對應的測試
- [ ] 測試覆蓋率 >= 80%
- [ ] 更新了相關的文檔
- [ ] 更新了 CHANGELOG.md
- [ ] 更新了 memory-bank/
- [ ] Commit message 遵循規範
- [ ] 沒有調試代碼或 print 語句

## 開發工作流

### 添加新的醫學工具

1. **建立 Tool Wrapper** (`medrax/tools/<tool_name>.py`)
   ```python
   from medrax.tools.base import BaseMedicalTool
   
   class YourToolService(BaseMedicalTool):
       def __init__(self, model_path: str):
           # 初始化醫學工具
           pass
       
       def process(self, image: np.ndarray) -> Dict:
           # 核心推理邏輯
           pass
   ```

2. **建立單元測試** (`tests/test_tools/test_your_tool.py`)
   ```python
   def test_your_tool_basic():
       # 測試基本功能
       pass
   ```

3. **整合到 Agent** (`medrax/agent/agent.py`)
   - 在 `tools` 字典中註冊新工具
   - 在 prompt 中說明工具用途

### 改進推理邏輯

1. **修改 Agent 提示詞** (`medrax/docs/system_prompts.txt`)
2. **測試推理效果** (`experiments/benchmark_medrax.ipynb`)
3. **記錄決策** (`memory-bank/decisionLog.md`)

## 代碼風格指南

### Python 代碼

```python
# Good - DDD 分離
class MedicalReasoningService:
    """Core reasoning logic"""
    def diagnose(self, findings: List[str]) -> Diagnosis:
        pass

class CheXagentWrapper(BaseMedicalTool):
    """Infrastructure - tool wrapper"""
    def process(self, image: np.ndarray) -> Dict:
        pass

# Bad - 混合關注點
def process_image_and_diagnose(image_path: str):
    # Infrastructure + Domain 混在一起
    pass
```

### 文檔字元串

```python
def some_medical_function(image: np.ndarray) -> Dict[str, Any]:
    """
    進行醫學影像分析。
    
    Args:
        image: 輸入的胸部 X 光影像 (HxWx3)
    
    Returns:
        包含分析結果的字典：
        - "findings": 列出的發現
        - "confidence": 信心分數 (0-1)
        - "metadata": 額外元資料
    
    Raises:
        ValueError: 如果影像格式不正確
    """
```

## 社群與支援

- 📧 問題與建議：開設 Issue
- 💬 討論：在 Pull Request 中評論
- 📖 文檔：參考 [CONSTITUTION.md](CONSTITUTION.md)

## 行為準則

請遵守 [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)。簡言之：

- 尊重他人，無論背景如何
- 提供建設性的反饋
- 專注於專業和友好的互動

## 許可證

貢獻代碼即表示您同意在 Apache License 2.0 下發佈您的代碼。
