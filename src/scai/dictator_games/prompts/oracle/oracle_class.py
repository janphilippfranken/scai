from pydantic import BaseModel


class OraclePrompt(BaseModel):
    """
    Assistant Prompt Class
    """
    id: str = "id of the assistant prompt"
    role: str = "system"
    system_message: str
    human_message: str