from pydantic import BaseModel


class MetaPrompt(BaseModel):
    """
    Meta Prompt Class
    """
    id: str = "id of the meta prompt"
    name: str = "name of the meta prompt"
    max_tokens: int = 200
    role: str = "user"

    content: str