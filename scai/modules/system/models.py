"""Models for the System Contract."""
from pydantic import BaseModel


class SystemContract(BaseModel):
    """Class for a system contract."""

    name: str = "contract/system message name"
    role: str = "system"

    content: str