"""
MCP Resources - Static resources and documentation

Resources provide documentation and reference information
accessible via MCP protocol.
"""

from typing import Any, Dict


def register_resources(app) -> None:
    """
    Register all MCP resources with the FastMCP app.
    
    Args:
        app: FastMCP application instance
    """
    
    @app.resource("medrax://info")
    def medrax_info() -> str:
        """
        General information about MedRAX medical imaging AI.
        """
        return """
# MedRAX - Medical Reasoning Agent for X-rays

MedRAX is an AI-powered medical imaging analysis system specialized
for chest X-ray interpretation.

## Capabilities

### 1. Pathology Classification
- 18 different pathologies using DenseNet-121
- Probability scores for each condition
- Trained on CheXpert, MIMIC-CXR, and NIH datasets

### 2. Visual Question Answering
- Natural language queries about X-rays
- Powered by CheXagent (Stanford AIMI)
- Supports multi-image comparison

### 3. Anatomical Segmentation
- 14 anatomical structures
- Quantitative measurements
- Visual overlay generation

### 4. DICOM Processing
- Full DICOM format support
- Window/level adjustment
- Metadata extraction

## Getting Started

1. **Register an image**: Use `register_image` with the file path
2. **Get the image_id**: Save the returned ID for analysis
3. **Run analysis**: Use classification, VQA, or segmentation tools
4. **Interpret results**: Follow clinical reasoning guidelines

## Safety Notice

MedRAX is designed to assist medical professionals, not replace them.
All findings should be verified by qualified radiologists.
"""
    
    @app.resource("medrax://pathologies")
    def pathology_reference() -> str:
        """
        Reference information for supported pathologies.
        """
        return """
# Chest X-Ray Pathology Reference

## Supported Pathologies (18)

### Cardiac
- **Cardiomegaly**: Enlarged heart silhouette
- **Enlarged Cardiomediastinum**: Widened mediastinal shadow

### Pulmonary
- **Atelectasis**: Partial or complete lung collapse
- **Consolidation**: Air space opacity (infection, hemorrhage, etc.)
- **Edema**: Pulmonary edema/fluid accumulation
- **Emphysema**: Hyperinflation with decreased markings
- **Infiltration**: Interstitial or alveolar infiltrates
- **Lung Lesion**: Focal lung abnormality
- **Lung Opacity**: Non-specific opacification
- **Mass**: Focal lesion > 3cm
- **Nodule**: Focal lesion < 3cm
- **Pneumonia**: Infectious consolidation

### Pleural
- **Effusion**: Pleural fluid collection
- **Pleural Thickening**: Thickened pleural surfaces
- **Pneumothorax**: Air in pleural space

### Other
- **Fibrosis**: Pulmonary fibrotic changes
- **Fracture**: Rib or clavicle fracture
- **Hernia**: Hiatal or diaphragmatic hernia

## Clinical Thresholds

| Finding | Low | Moderate | High |
|---------|-----|----------|------|
| General | <0.3 | 0.3-0.6 | >0.6 |
| Urgent* | <0.2 | 0.2-0.4 | >0.4 |

*Urgent findings (Pneumothorax, large Effusion) use lower thresholds
"""
    
    @app.resource("medrax://organs")
    def organ_reference() -> str:
        """
        Reference information for supported anatomical structures.
        """
        return """
# Anatomical Structure Reference

## Supported Structures (14)

### Skeletal
- **Left/Right Clavicle**: Collar bones
- **Left/Right Scapula**: Shoulder blades
- **Spine**: Vertebral column

### Pulmonary
- **Left/Right Lung**: Main lung fields
- **Left/Right Hilus Pulmonis**: Lung roots (vessels, bronchi)

### Cardiac/Vascular
- **Heart**: Cardiac silhouette
- **Aorta**: Aortic arch and descending aorta

### Mediastinal
- **Mediastinum**: Central chest cavity
- **Weasand**: Esophagus (trachea region)
- **Facies Diaphragmatica**: Diaphragm surface

## Measurement Guidelines

### Cardiothoracic Ratio (CTR)
- CTR = Heart width / Thoracic width
- Normal: < 0.5 on PA view
- Cardiomegaly: ≥ 0.5

### Lung Volumes
- Compare left vs right for asymmetry
- Consider positioning and inspiration depth

### Mediastinal Width
- Should be < 8cm on PA view
- Widening may indicate mass, lymphadenopathy, or vascular abnormality
"""
    
    @app.resource("medrax://workflow")
    def workflow_guide() -> str:
        """
        Recommended workflow for chest X-ray analysis.
        """
        return """
# Recommended Analysis Workflow

## Standard Workflow

### Step 1: Image Preparation
```
# For standard images (PNG, JPEG)
register_image("/path/to/chest_xray.png")
→ Returns: image_id

# For DICOM files
process_dicom("/path/to/study.dcm")
→ Returns: image_id + metadata
```

### Step 2: Initial Classification
```
classify_cxr(image_id, threshold=0.3)
→ Returns: pathology probabilities
```

### Step 3: Targeted Analysis
Based on classification results:

**If cardiac findings:**
```
segment_anatomy(image_id, organs=["Heart", "Aorta"])
ask_cxr_expert(image_id, "Describe the cardiac silhouette")
```

**If pulmonary findings:**
```
segment_anatomy(image_id, organs=["Left Lung", "Right Lung"])
ask_cxr_expert(image_id, "Describe any pulmonary abnormalities")
```

### Step 4: Generate Report
```
ask_cxr_expert(image_id, "Generate a radiology report for this chest X-ray")
```

## Comparison Workflow

For follow-up studies:
```
# Register both images
id1 = register_image("/path/to/baseline.png")
id2 = register_image("/path/to/followup.png")

# Compare
ask_cxr_expert([id1, id2], "Compare these X-rays and describe changes")
```

## Emergency Workflow

For urgent cases, check critical findings first:
```
result = classify_cxr(image_id, 
    pathologies=["Pneumothorax", "Effusion", "Pneumonia"],
    threshold=0.3)
```
"""
