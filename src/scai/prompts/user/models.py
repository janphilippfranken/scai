from pydantic import BaseModel


class UserPrompt(BaseModel):
    """
    User Prompt Class
    """
    id: str = "id of the user prompt"
    name: str = "name of the user prompt"
    persona_short: str = "persona short description"
    persona: str = "persona description"
    task_connectives: dict
    role: str = "system"

    content: str

class UserTemplate():
    """
    User Template Class
    """
    id: str = "template id"
    name: str = "name of the template"
    content_user_gen: str # user generation template
    content_user_con: str # task connectives generation template
