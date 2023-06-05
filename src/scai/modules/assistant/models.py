"""Models for the Assistant Prompt."""
from pydantic import BaseModel


class AssistantPrompt(BaseModel):
    """Class for a assistant system prompt (i.e. the contract)."""

    name: str = "assistant prompttname"
    role: str = "system"

    content: str