"""
The Task Prompt.
"""
from typing import Dict, List
    
from scai.metrics.models import MetricPrompt

METRIC_PROMPT: Dict[str, MetricPrompt] = {
    "metric_prompt_1": MetricPrompt(
        name="satisfaction",
        metrics = ["Satisfaction", "Feedback"],
        content="""To make my draft more appealing to your persona and raise your satisfaction for future drafts, could you rate your current satisfaction from 0-10 (0 being not satisfied at all, 10 fully satisfied), and provide short, constructive feedback? This feedback will guide my revisions to increase your satisfaction in the future. Please use this format:
Satisfaction: <Rate from 0-10>
Feedback: <Persona-based suggestions for improvement in less than {max_tokens} tokens>"""
    ),
}