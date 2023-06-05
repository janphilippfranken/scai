"""Models for the User Prompt."""
from pydantic import BaseModel


class UserPrompt(BaseModel):
    """Class for a User prompt (i.e. contract / persona)."""

    name: str = "user prompt name"
    role: str = "system"

    content: str