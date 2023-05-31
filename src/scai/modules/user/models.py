"""Models for the User Contract."""
from pydantic import BaseModel


class UserContract(BaseModel):
    """Class for a User contract."""

    name: str = "user contrac name"
    role: str = "system"

    content: str