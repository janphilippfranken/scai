from pydantic import BaseModel


class AssistantPrompt(BaseModel):
    """
    Assistant Prompt Class
    """
    id: str = "id of the assistant prompt"
    name: str = "name of the assistant prompt"
    role: str = "system"

    content: str