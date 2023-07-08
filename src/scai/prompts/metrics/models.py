from typing import List

from pydantic import BaseModel


class MetricPrompt(BaseModel):
    """
    Metrics to collect
    """
    name: str = "name of metric"
    subjective_metric: str = "metric to collect from user rating the assistant in their own conversation"
    collective_metric: str = "metric to collect from users rating the assistant in other conversations"

    subjective_content: str
    collective_content: str 