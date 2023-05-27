"""Models for the SCAI user chain."""
from pydantic import BaseModel


class SCAIUser(BaseModel):
    """Class for a SCAI user."""

    
    name: str = "SCAI User"