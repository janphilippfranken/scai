"""Models for the Assistant Contract."""
from pydantic import BaseModel


class AssistantContract(BaseModel):
    """Class for a assistant contract."""

    name: str = "contract/assistant message name"
    role: str = "assistant"

    content: str