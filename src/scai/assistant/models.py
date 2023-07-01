from pydantic import BaseModel


class AssistantPrompt(BaseModel):
    """
    Assistant Prompt Class
    """
    id: str = "id of the assistant prompt"
    name: str = "name of the assistant prompt"
    max_tokens: int = 100
    role: str = "system"

    content: str