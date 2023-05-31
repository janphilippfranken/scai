"""Models for meta-prompt."""
from pydantic import BaseModel


class MetaPrompt(BaseModel):
    """Class for a metapormpt."""

    name: str = "meta_prompt"
    role: str = "system"

    content: str