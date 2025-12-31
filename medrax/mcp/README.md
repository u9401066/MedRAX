# MedRAX MCP Server

> Model Context Protocol (MCP) Server for MedRAX Medical Imaging AI

## 概述

MedRAX MCP Server 將 MedRAX 的醫學影像分析能力透過 MCP 協議暴露給 AI 代理（如 GitHub Copilot、Claude Desktop、Cline 等）。

## 架構

採用 **DDD (Domain-Driven Design)** 四層架構：

```
medrax/mcp/
├── domain/           # 核心實體與協議
│   ├── entities.py   # ImageEntity, ClassificationResult, etc.
│   ├── protocols.py  # ClassifierProtocol, VQAProtocol, etc.
│   └── exceptions.py # MedRAXError 異常層級
│
├── infrastructure/   # 工具包裝器
│   ├── classifier.py     # DenseNet-121 分類器
│   ├── vqa.py            # CheXagent VQA
│   ├── segmentation.py   # PSPNet 分割
│   ├── dicom.py          # DICOM 處理
│   └── image_storage.py  # 圖像存儲服務
│
├── application/      # 應用服務層
│   └── services.py   # ClassificationService, VQAService, etc.
│
├── presentation/     # MCP 暴露層
│   ├── tools.py      # FastMCP 工具定義
│   ├── prompts.py    # 臨床推理提示
│   └── resources.py  # 靜態資源與文檔
│
└── server.py         # 主伺服器入口
```

## 安裝

```bash
# 安裝 MCP 依賴
pip install medrax[mcp]

# 或手動安裝
pip install mcp>=1.0.0
```

## 使用方式

### 1. 命令列啟動

```bash
# 使用 stdio 傳輸（適合 VS Code Copilot）
medrax-mcp

# 指定設備
medrax-mcp --device cuda

# 預載入所有模型
medrax-mcp --eager-load

# 使用 SSE 傳輸
medrax-mcp --transport sse
```

### 2. VS Code Copilot 設定

在 VS Code `settings.json` 中加入：

```json
{
  "github.copilot.chat.codeGeneration.instructions": [
    {
      "text": "Use @medrax for medical image analysis"
    }
  ],
  "mcp.servers": {
    "medrax": {
      "command": "medrax-mcp",
      "args": ["--device", "cuda"]
    }
  }
}
```

### 3. Claude Desktop 設定

在 `claude_desktop_config.json` 中加入：

```json
{
  "mcpServers": {
    "medrax": {
      "command": "medrax-mcp",
      "args": []
    }
  }
}
```

## 可用工具

### 圖像管理

| 工具 | 描述 |
|------|------|
| `register_image` | 註冊本地圖像檔案，獲取 image_id |
| `process_dicom` | 處理 DICOM 檔案並轉換為標準格式 |
| `get_dicom_metadata` | 提取 DICOM 元資料 |
| `list_registered_images` | 列出所有已註冊圖像 |

### 分析工具

| 工具 | 描述 |
|------|------|
| `classify_cxr` | 18 種病理分類 (DenseNet-121) |
| `ask_cxr_expert` | 視覺問答 (CheXagent) |
| `segment_anatomy` | 14 種解剖結構分割 (PSPNet) |

### 參考資訊

| 工具 | 描述 |
|------|------|
| `get_supported_pathologies` | 獲取支援的病理列表 |
| `get_supported_organs` | 獲取支援的器官列表 |

## 使用範例

### 基本工作流程

```
User: 分析這張胸部 X 光 /data/chest_xray.png

Copilot:
1. register_image("/data/chest_xray.png")
   → image_id: "img_abc123"

2. classify_cxr("img_abc123", threshold=0.3)
   → {
       "positive_findings": {"Cardiomegaly": 0.72, "Effusion": 0.45},
       "top_findings": [...]
     }

3. segment_anatomy("img_abc123", organs=["Heart", "Left Lung", "Right Lung"])
   → {
       "organ_metrics": {...},
       "visualization": "base64..."
     }

4. 根據 clinical_reasoning prompt 生成報告
```

### DICOM 處理

```
User: 處理這個 DICOM 檔案 /data/study.dcm

Copilot:
1. process_dicom("/data/study.dcm")
   → {
       "image_id": "img_xyz789",
       "metadata": {
         "patient_id": "P001",
         "modality": "CR",
         "study_date": "20240101"
       }
     }

2. classify_cxr("img_xyz789")
   → ...
```

## MCP Prompts

伺服器提供以下提示模板：

- **clinical_reasoning**: 臨床推理指南
- **classification_interpretation**: 分類結果解讀
- **segmentation_interpretation**: 分割結果解讀
- **vqa_interpretation**: VQA 結果解讀

## MCP Resources

靜態資源：

- `medrax://info`: 系統概述
- `medrax://pathologies`: 病理參考
- `medrax://organs`: 器官參考
- `medrax://workflow`: 建議工作流程

## 開發

### 執行測試

```bash
pytest tests/mcp/ -v
```

### 本地開發

```python
from medrax.mcp import create_mcp_app

# 創建應用
app = create_mcp_app(device="cuda", lazy_load=True)

# 手動測試工具
from medrax.mcp.application.services import MedRAXServiceContainer
services = MedRAXServiceContainer(device="cuda")

# 註冊圖像
image_id = services.register_image("/path/to/image.png")

# 分類
result = services.classification.classify(image_id)
print(result)
```

## 安全注意事項

⚠️ **MedRAX 為 AI 輔助工具，非診斷工具**

- 所有結果應由合格放射科醫師審核
- AI 分析僅供參考，不能替代臨床判斷
- 關鍵發現需要臨床關聯確認

## 授權

MIT License - 詳見 [LICENSE](../../LICENSE)
