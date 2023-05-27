"""Models for the SCAI System chain."""
from pydantic import BaseModel


class scaiSystem(BaseModel):
    """Class for a SCAI System."""
    
    name: str = "SCAI System"