from pydantic import BaseModel


class AssistantPrompt(BaseModel):
    """
    Assistant Prompt Class
    """
    id: str = "id of the assistant prompt"
    role: str = "system"
    manners: str = "manners description: polite, rude, or neutral"
    content: str