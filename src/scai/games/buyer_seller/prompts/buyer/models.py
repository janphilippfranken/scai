from pydantic import BaseModel


class BuyerPompt(BaseModel):
    """
    Buyer Prompt
    """
    id: str = "id of the prompt"
    role: str = "system"
    content: str
    strategy: str