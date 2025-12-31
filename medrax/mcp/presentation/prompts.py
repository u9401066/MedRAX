"""
MCP Prompts - Reusable prompt templates for clinical reasoning

These prompts guide the LLM (Copilot/Claude) on how to interpret
and present medical imaging results.
"""

from typing import Any, Dict


def register_prompts(app) -> None:
    """
    Register all MCP prompts with the FastMCP app.
    
    Args:
        app: FastMCP application instance
    """
    
    @app.prompt()
    def clinical_reasoning() -> str:
        """
        Guidelines for clinical interpretation of chest X-ray analysis results.
        
        Use this prompt when analyzing medical images to ensure
        proper clinical context and responsible AI usage.
        """
        return """
# Clinical Reasoning Guidelines for Chest X-Ray Analysis

When analyzing medical images using MedRAX tools, follow these principles:

## 1. INTERPRET Results in Clinical Context
- Explain the clinical significance of findings, not just numbers
- Compare probabilities against clinical thresholds
- Consider the patient's clinical presentation if known

## 2. INTEGRATE Multiple Tool Outputs
- Correlate classification results with segmentation findings
- Cross-reference anatomical measurements
- Note any discrepancies between different analyses

## 3. PROVIDE Structured Clinical Interpretation
Format your response with:
- **Findings**: Objective observations from the analysis
- **Impression**: Clinical interpretation of findings
- **Recommendations**: Suggested follow-up or additional imaging

## 4. ACKNOWLEDGE Limitations
- AI analysis is supportive, not diagnostic
- Always recommend clinical correlation
- Note technical limitations (image quality, positioning)
- Mention when findings are equivocal or uncertain

## 5. ENSURE Patient Safety
- Flag critical findings prominently (pneumothorax, large effusion)
- Recommend urgent review when appropriate
- Never provide definitive diagnoses without clinical context

## Example Response Format:

### Chest X-Ray Analysis

**Findings:**
- Classification detected elevated probability for [pathology] (XX%)
- Segmentation shows [anatomical observation]
- [Additional relevant findings]

**Impression:**
[Clinical interpretation of the findings]

**Recommendations:**
1. [Primary recommendation]
2. [Secondary recommendation if applicable]

**Limitations:**
- [Any technical or analytical limitations]

---
*This analysis is AI-assisted and should be reviewed by a qualified radiologist.*
"""
    
    @app.prompt()
    def classification_interpretation() -> str:
        """
        How to interpret chest X-ray classification results.
        """
        return """
# Interpreting Chest X-Ray Classification Results

## Understanding Probability Scores
- **0.0 - 0.3**: Low probability, unlikely to be present
- **0.3 - 0.5**: Moderate probability, may warrant further review
- **0.5 - 0.7**: Elevated probability, likely present
- **0.7 - 1.0**: High probability, strong indication

## Key Pathologies and Clinical Significance

### Urgent Findings (require immediate attention)
- **Pneumothorax**: Air in pleural space, may need decompression
- **Large Effusion**: Fluid accumulation, may compromise breathing
- **Consolidation**: May indicate pneumonia or other acute process

### Important Findings
- **Cardiomegaly**: Enlarged heart, may indicate heart failure
- **Pulmonary Edema**: Fluid in lungs, often with heart failure
- **Mass/Nodule**: May require cancer workup

### Common Findings
- **Atelectasis**: Partial lung collapse, often positional
- **Pleural Thickening**: May be chronic or post-inflammatory

## Reporting Guidelines
1. List findings in order of clinical importance
2. Note the probability score for each finding
3. Correlate related findings (e.g., cardiomegaly + edema)
4. Recommend appropriate follow-up
"""
    
    @app.prompt()
    def segmentation_interpretation() -> str:
        """
        How to interpret anatomical segmentation results.
        """
        return """
# Interpreting Anatomical Segmentation Results

## Understanding Metrics

### Area Measurements
- **area_pixels**: Raw pixel count (use for relative comparisons)
- **area_cm2**: Approximate physical area (accurate only with DICOM)

### Position Metrics
- **centroid**: Center point of the segmented region
- **relative_position**: Position relative to image boundaries (0-1 scale)

### Quality Indicators
- **confidence_score**: Model confidence (higher = more reliable)
- **mean_intensity**: Average brightness in the region

## Clinical Applications

### Cardiac Assessment
- **Heart size**: Compare to thoracic width (cardiothoracic ratio)
- Normal CTR < 0.5 in PA view

### Lung Assessment
- **Lung volumes**: Asymmetry may indicate pathology
- **Hilar regions**: Enlarged may indicate lymphadenopathy

### Mediastinal Assessment
- **Mediastinum width**: Widening may indicate mass or vascular abnormality
- **Aorta**: Calcification or dilation assessment

## Important Notes
- Area calculations are approximate without proper pixel spacing
- Segmentation quality depends on image quality and positioning
- Always correlate with clinical findings
"""
    
    @app.prompt()
    def vqa_interpretation() -> str:
        """
        How to interpret visual question answering results.
        """
        return """
# Interpreting VQA (Visual Question Answering) Results

## Understanding CheXagent Responses

CheXagent is a specialized model for chest X-ray analysis. Its responses:
- Are based on visual features in the image
- May include medical terminology
- Should be verified against classification/segmentation results

## Best Practices for Questions

### Effective Questions
- "What abnormalities are visible in this chest X-ray?"
- "Is there evidence of pneumonia?"
- "Describe the cardiac silhouette"
- "Compare the lung fields bilaterally"

### Questions to Avoid
- Overly specific clinical questions without context
- Questions about patient history (model doesn't have access)
- Definitive diagnostic questions

## Interpreting Responses

1. **Correlation**: Cross-check VQA answers with classification results
2. **Confidence**: Note when the model expresses uncertainty
3. **Completeness**: VQA may not mention all findings - use classification
4. **Context**: Add clinical context when presenting to users

## Limitations
- Model may miss subtle findings
- May hallucinate details not in the image
- Should not be used as sole diagnostic tool
"""
