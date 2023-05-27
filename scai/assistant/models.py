"""Models for the SCAI Assistant chain."""
from pydantic import BaseModel


class SCAIAssistant(BaseModel):
    """Class for a SCAI Assistant."""

    
    name: str = "SCAI Assistant"