"""Models for the Assistant Contract."""
from pydantic import BaseModel


class AssistantContract(BaseModel):
    """Class for a assistant contract."""

    name: str = "assistant contract name"
    role: str = "system"

    content: str