from pydantic import BaseModel


class UserPrompt(BaseModel):
    """
    User Prompt Class
    """
    id: str = "id of the user prompt"
    name: str = "name of the user prompt"
    persona: str = "persona description"
    role: str = "system"

    content: str