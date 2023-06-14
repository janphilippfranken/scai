"""Models for meta-prompt."""
from pydantic import BaseModel


class MetaPrompt(BaseModel):
    """Class for a metapormpt."""

    id: str = "id of the meta prompt"
    name: str = "name of the meta prompt"
    max_tokens: int = 100
    persona: str = "the meta persona"
    role: str = "system"

    content: str