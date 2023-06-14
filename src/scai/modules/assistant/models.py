"""Models for the Assistant Prompt."""
from pydantic import BaseModel


class AssistantPrompt(BaseModel):
    """Class for a assistant system prompt (i.e. the contract)."""

    id: str = "id of the assistant prompt"
    name: str = "name of the assistant prompt"
    max_tokens: int = 100
    role: str = "system"

    content: str