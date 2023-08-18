from pydantic import BaseModel


class SellerPrompt(BaseModel):
    """
    Seller Prompt
    """
    id: str = "id of the prompt"
    role: str = "system"
    content: str
    strategy: str