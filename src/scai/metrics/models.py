from pydantic import BaseModel


class MetricPrompt(BaseModel):
    """
    Metrics to collect
    """
    name: str = "name of metric"

    content: str