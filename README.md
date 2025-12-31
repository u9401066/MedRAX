<h1 align="center">
🚀 MedRAX Plus: Advanced Multi-Modal Medical Reasoning Agent
</h1>
<p align="center">
<em>Extended fork of the original MedRAX with EKG support, modern architecture, and interactive UI</em>
</p>
<p align="center"> <a href="https://arxiv.org/abs/2502.02673" target="_blank"><img src="https://img.shields.io/badge/arXiv-ICML 2025-FF6B6B?style=for-the-badge&logo=arxiv&logoColor=white" alt="arXiv"></a> <a href="https://github.com/u9401066/MedRAX"><img src="https://img.shields.io/badge/GitHub-MedRAX Plus-4A90E2?style=for-the-badge&logo=github&logoColor=white" alt="GitHub"></a> <a href="https://github.com/bowang-lab/MedRAX"><img src="https://img.shields.io/badge/Original-bowang--lab-lightgrey?style=for-the-badge&logo=github&logoColor=white" alt="Original"></a> <a href="https://huggingface.co/datasets/wanglab/chest-agent-bench"><img src="https://img.shields.io/badge/HuggingFace-Dataset-FFBF00?style=for-the-badge&logo=huggingface&logoColor=white" alt="HuggingFace Dataset"></a> </p>

![](assets/demo_fast.gif?autoplay=1)

<br>

## 🌟 What is MedRAX Plus?

**MedRAX Plus** is an advanced extension of the original MedRAX that adds:

- **EKG/ECG Analysis** - Full cardiac signal support
- **Modern LangGraph Architecture** - State-based agent orchestration
- **Interactive Region-Aware UI** - Real-time marking and spatial context
- **Multi-Interface Deployment** - Gradio + MCP Server + VS Code Copilot
- **Constitutional AI Framework** - DDD architecture + 13 Claude Skills
- **Multi-Modal Joint Reasoning** - Advanced cardiopulmonary analysis

### Quick Comparison

| Feature | Original MedRAX | MedRAX Plus |
|---------|-----------------|-------------|
| **CXR Analysis** | ✅ | ✅ Enhanced |
| **EKG/ECG Analysis** | ❌ | ✅ NEW |
| **Agent Type** | Linear LangChain | **LangGraph State-Based** |
| **UI Interaction** | Static upload | **Dynamic region marking** |
| **Deployment** | Gradio only | **Gradio + MCP + Copilot** |
| **Code Architecture** | Standard | **Constitutional (DDD)** |
| **Development Tools** | None | **13 Claude Skills** |
| **Multi-Modal Fusion** | Basic | **Advanced reasoning** |

<br>

## 🌟 MedRAX Plus Features

**Multi-Modal Analysis**
- 🖼️ CXR (2D images) - Comprehensive radiological interpretation
- 📡 EKG/ECG (time-series signals) - Cardiac signal processing and classification
- 🧠 Joint Reasoning - Integrated cardiopulmonary decision support

**Modern Architecture**
- 🏗️ **LangGraph**: State-based agent with conditional routing
- 🔄 **Tool Use Protocol**: Modern Anthropic/OpenAI-style tool integration
- 📊 **State Management**: Rich clinical context and reasoning traces
- 🎯 **Multi-Path Orchestration**: CXR, EKG, or combined analysis routes

**Interactive User Experience**
- 🖱️ **Region Marking**: Draw boxes/circles on images to focus analysis
- 🎤 **Multi-Modal Input**: Text, voice, and visual annotations
- 📍 **Spatial Awareness**: Agent understands marked regions and attention
- ⚡ **Real-Time Feedback**: Streaming responses with confidence scores

**Deployment Flexibility**
- 🌐 **Gradio Web UI**: Production-ready interface with interactive features
- 🤖 **MCP Server**: Claude and other LLM integration via Model Context Protocol
- 💻 **VS Code Copilot**: IDE-native medical image analysis (@medrax commands)
- 🏥 **Local or Cloud**: Supports both deployment models

**AI-Assisted Development**
- 📜 **Constitutional Framework**: Hierarchical rules (CONSTITUTION > Bylaws > Skills)
- 🧠 **Memory Bank**: Cross-session project knowledge management
- 🤖 **13 Claude Skills**: Automated code review, testing, documentation
- 🏛️ **DDD Architecture**: Clean, maintainable medical domain logic

<br>

## Abstract (Original CXR Paper)
Chest X-rays (CXRs) play an integral role in driving critical decisions in disease management and patient care. While recent innovations have led to specialized models for various CXR interpretation tasks, these solutions often operate in isolation, limiting their practical utility in clinical practice. We present MedRAX, the first versatile AI agent that seamlessly integrates state-of-the-art CXR analysis tools and multimodal large language models into a unified framework. MedRAX dynamically leverages these models to address complex medical queries without requiring additional training. To rigorously evaluate its capabilities, we introduce ChestAgentBench, a comprehensive benchmark containing 2,500 complex medical queries across 7 diverse categories. Our experiments demonstrate that MedRAX achieves state-of-the-art performance compared to both open-source and proprietary models, representing a significant step toward the practical deployment of automated CXR interpretation systems.
<br><br>


## MedRAX Plus Architecture
Built on robust modern foundations:
- **Core Framework**: LangChain + LangGraph (stateful agent orchestration)
- **Language Model**: GPT-4o with vision + multi-modal reasoning
- **Multi-Modal Support**: CXR (images) + EKG (time-series signals)
- **Deployment Options**: Gradio web, MCP server, VS Code Copilot extension
- **UI Framework**: Interactive Gradio with Canvas annotation
- **Design Pattern**: DDD (Domain-Driven Design) architecture
- **Development Workflow**: Constitutional framework + Claude Skills

### CXR Tool Suite
- **Visual QA**: CheXagent, LLaVA-Med
- **Segmentation**: MedSAM, PSPNet

- **Grounding**: Maira-2 (region localization)
- **Report Generation**: SwinV2 + CheXpert Plus
- **Classification**: DenseNet-121 + TorchXRayVision (18 pathologies)
- **Synthesis**: RoentGen (synthetic generation)
- **Utilities**: DICOM processing, visualization tools

### EKG/ECG Tools (v0.2.0+)
- **Signal Processing**: R-peak detection, HRV analysis, ECG-SQI
- **Classification**: ResNet-ECG, Transformer-based models
- **Arrhythmia Detection**: ArrhythmiaNet, pattern matching
- **Report Generation**: ECG-BERT (clinical reports)
- **Risk Assessment**: Integrated scoring systems

### Multi-Modal Reasoning
- **Joint Analysis**: CXR + EKG integration for cardiopulmonary conditions
- **Clinical Context**: Synchronized interpretation of imaging and signals
- **Recommendation Engine**: Unified decision support
<br><br>


## ChestAgentBench
We introduce ChestAgentBench, a comprehensive evaluation framework with 2,500 complex medical queries across 7 categories, built from 675 expert-curated clinical cases. The benchmark evaluates complex multi-step reasoning in CXR interpretation through:

- Detection
- Classification
- Localization
- Comparison
- Relationship
- Diagnosis
- Characterization

Download the benchmark: [ChestAgentBench on Hugging Face](https://huggingface.co/datasets/wanglab/chest-agent-bench)
```
huggingface-cli download wanglab/chestagentbench --repo-type dataset --local-dir chestagentbench
```

Unzip the Eurorad figures to your local `MedMAX` directory.
```
unzip chestagentbench/figures.zip
```

To evaluate with GPT-4o, set your OpenAI API key and run the quickstart script.
```
export OPENAI_API_KEY="<your-openai-api-key>"
python quickstart.py \
    --model chatgpt-4o-latest \
    --temperature 0.2 \
    --max-cases 2 \
    --log-prefix chatgpt-4o-latest \
    --use-urls
```


<br>

## Installation
### Prerequisites
- Python 3.10+
- CUDA/GPU for best performance
- [uv](https://docs.astral.sh/uv/) - 現代Python包管理器

### Installation Steps
```bash
# Clone the repository
git clone https://github.com/bowang-lab/MedRAX.git
cd MedRAX

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Setup environment and install dependencies
uv sync

# Activate the virtual environment
source .venv/bin/activate

# Or use uv run to execute commands directly
uv run python main.py
```

### Quick Start with uv
```bash
# Run the Gradio interface directly with uv
uv run python main.py

# Or install as a package and run
uv run --with dev --extras test medrax

# Run benchmarks
uv run python quickstart.py \
    --model chatgpt-4o-latest \
    --temperature 0.2 \
    --max-cases 2 \
    --log-prefix chatgpt-4o-latest \
    --use-urls
```

### Development Setup
```bash
# Install with development dependencies
uv sync --extra dev

# Install pre-commit hooks
uv run pre-commit install

# Run tests
uv run pytest

# Format code
uv run black .
uv run isort .
```

### MCP Server (VS Code Copilot Integration)

MedRAX supports the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) for seamless integration with VS Code Copilot and other LLM agents.

```bash
# Run MCP Server (stdio transport for VS Code)
uv run python -m medrax.mcp.server --device cuda --transport stdio

# Or with SSE transport for web clients
uv run python -m medrax.mcp.server --device cuda --transport sse --port 8000
```

#### VS Code Configuration
Add to `.vscode/mcp.json`:
```json
{
  "servers": {
    "medrax": {
      "type": "stdio",
      "command": "${workspaceFolder}/.venv/bin/python",
      "args": ["-m", "medrax.mcp.server", "--device", "cuda", "--transport", "stdio"],
      "env": {"PYTHONPATH": "${workspaceFolder}"}
    }
  }
}
```

#### Available MCP Tools
| Tool | Description |
|------|-------------|
| `register_image` | Register a local image for analysis |
| `process_dicom` | Convert DICOM to viewable format |
| `get_dicom_metadata` | Extract DICOM metadata |
| `classify_cxr` | Classify 18 pathologies |
| `segment_anatomy` | Segment 14 anatomical structures |
| `ask_cxr_expert` | Visual QA with CheXagent |
| `get_supported_pathologies` | List supported pathologies |
| `get_supported_organs` | List supported organs |
| `list_registered_images` | List registered images |
<br><br><br>


## Tool Selection and Initialization

MedRAX supports selective tool initialization, allowing you to use only the tools you need. Tools can be specified when initializing the agent (look at `main.py`):

```python
selected_tools = [
    "ImageVisualizerTool",
    "ChestXRayClassifierTool",
    "ChestXRaySegmentationTool",
    # Add or remove tools as needed
]

agent, tools_dict = initialize_agent(
    "medrax/docs/system_prompts.txt",
    tools_to_use=selected_tools,
    model_dir="/model-weights"
)
```

<br><br>
## Automatically Downloaded Models

The following tools will automatically download their model weights when initialized:

### Classification Tool
```python
ChestXRayClassifierTool(device=device)
```

### Segmentation Tool
```python
ChestXRaySegmentationTool(device=device)
```

### Grounding Tool
```python
XRayPhraseGroundingTool(
    cache_dir=model_dir, 
    temp_dir=temp_dir, 
    load_in_8bit=True, 
    device=device
)
```
- Maira-2 weights download to specified `cache_dir`
- 8-bit and 4-bit quantization available for reduced memory usage

### LLaVA-Med Tool
```python
LlavaMedTool(
    cache_dir=model_dir, 
    device=device, 
    load_in_8bit=True
)
```
- Automatic weight download to `cache_dir`
- 8-bit and 4-bit quantization available for reduced memory usage

### Report Generation Tool
```python
ChestXRayReportGeneratorTool(
    cache_dir=model_dir, 
    device=device
)
```

### Visual QA Tool
```python
XRayVQATool(
    cache_dir=model_dir, 
    device=device
)
```
- CheXagent weights download automatically

### MedSAM Tool
```
Support for MedSAM segmentation will be added in a future update.
```

### Utility Tools
No additional model weights required:
```python
ImageVisualizerTool()
DicomProcessorTool(temp_dir=temp_dir)
```
<br>

## Manual Setup Required

### Image Generation Tool
```python
ChestXRayGeneratorTool(
    model_path=f"{model_dir}/roentgen", 
    temp_dir=temp_dir, 
    device=device
)
```
- RoentGen weights require manual setup:
  1. Contact authors: https://github.com/StanfordMIMI/RoentGen
  2. Place weights in `{model_dir}/roentgen`
  3. Optional tool, can be excluded if not needed
<br>

## Configuration Notes

### Required Parameters
- `model_dir` or `cache_dir`: Base directory for model weights that Hugging Face uses
- `temp_dir`: Directory for temporary files
- `device`: "cuda" for GPU, "cpu" for CPU-only

### Memory Management
- Consider selective tool initialization for resource constraints
- Use 8-bit quantization where available
- Some tools (LLaVA-Med, Grounding) are more resource-intensive
<br>

### Local LLMs
If you are running a local LLM using frameworks like [Ollama](https://ollama.com/) or [LM Studio](https://lmstudio.ai/), you need to configure your environment variables accordingly. For example:
```
export OPENAI_BASE_URL="http://localhost:11434/v1"
export OPENAI_API_KEY="ollama"
```
<br>

### Optional: OpenAI-compatible Providers

MedRAX supports OpenAI-compatible APIs, allowing regional or local LLM providers to serve as alternative backends.

For example, to use **Qwen3-VL** via [Alibaba Cloud DashScope](https://bailian.console.aliyun.com/?tab=model#/model-market), set the following environment variables:

```bash
export OPENAI_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
export OPENAI_API_KEY="<your-dashscope-api-key>"
export OPENAI_MODEL="qwen3-vl-235b-a22b-instruct"
```
<br>

## Star History
<div align="center">
  
[![Star History Chart](https://api.star-history.com/svg?repos=bowang-lab/MedRAX&type=Date)](https://star-history.com/#bowang-lab/MedRAX&Date)

</div>
<br>


## Authors
- **Adibvafa Fallahpour**¹²³⁴ * (adibvafa.fallahpour@mail.utoronto.ca)
- ****Jun Ma****²³ *
- **Alif Munim**³⁵ *
- ****Hongwei Lyu****³
- ****Bo Wang****¹²³⁶

¹ Department of Computer Science, University of Toronto, Toronto, Canada <br>
² Vector Institute, Toronto, Canada <br>
³ University Health Network, Toronto, Canada <br>
⁴ Cohere, Toronto, Canada <br>
⁵ Cohere Labs, Toronto, Canada <br>
⁶ Department of Laboratory Medicine and Pathobiology, University of Toronto, Toronto, Canada

<br>
* Equal contribution
<br><br>


## Citation
If you find this work useful, please cite our paper:
```bibtex
@misc{fallahpour2025medraxmedicalreasoningagent,
      title={MedRAX: Medical Reasoning Agent for Chest X-ray}, 
      author={Adibvafa Fallahpour and Jun Ma and Alif Munim and Hongwei Lyu and Bo Wang},
      year={2025},
      eprint={2502.02673},
      archivePrefix={arXiv},
      primaryClass={cs.LG},
      url={https://arxiv.org/abs/2502.02673}, 
}
```

---
<p align="center">
Made with ❤️ at University of Toronto, Vector Institute, and University Health Network
</p>
