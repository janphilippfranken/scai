from typing import List

from pydantic import BaseModel


class MetricPrompt(BaseModel):
    """
    Metrics to collect
    """
    name: str = "name of metric"
    metrics: List[str] = ["list of metrics to collect from user"]

    content: str