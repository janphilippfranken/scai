from typing import List

from pydantic import BaseModel


class MetricPrompt(BaseModel):
    """
    Metrics to collect
    """
    name: str = "name of metric"
    metrics: List[str] = ["list of metrics to collect from user based on own conversation"]
    metrics_other: List[str] = ["list of metrics to collect from user based on other conversation (i.e. rate assitant's interaction with other users)"]

    content: str
    content_other: str 