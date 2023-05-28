"""Models for the User Contract."""
from pydantic import BaseModel


class UserContract(BaseModel):
    """Class for a User contract."""

    name: str = "contract/user message name"
    role: str = "user"

    content: str