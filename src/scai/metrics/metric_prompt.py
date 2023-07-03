"""
The Task Prompt.
"""
from typing import Dict, List
    
from scai.metrics.models import MetricPrompt

METRIC_PROMPT: Dict[str, MetricPrompt] = {
    "metric_prompt_1": MetricPrompt(
        name="satisfaction",
        metrics = ["Satisfaction", "Feedback"],
        content="""To improve my future performance on this task, please evaluate my current attempt as follows:
Satisfaction: <Rate from 0-10>
Feedback: <Please provide suggestions that could help me better complete this task in the future and increase your satisfaction, using less than {max_tokens} tokens.>"""
    ),
}