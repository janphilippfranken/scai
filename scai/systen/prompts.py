"""Models for the SCAI System Chain."""
from pydantic import BaseModel


class SCAISystem(BaseModel):
    """Class for a SCAI System."""

    
    name: str = "SCAI System"