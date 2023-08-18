from pydantic import BaseModel


class BuyerPrompt(BaseModel):
    """
    Buyer Prompt
    """
    id: str = "id of the prompt"
    role: str = "system"
    content: str
    strategy: str