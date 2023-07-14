from pydantic import BaseModel
from langchain.prompts import HumanMessagePromptTemplate


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

class UserTemplate(BaseModel):
    """
    User Template Class
    """
    id: str = "template id"
    name: str = "name of the template"
    content_user_gen: HumanMessagePromptTemplate = "user generation template"
    content_user_con: HumanMessagePromptTemplate =  "task connectives generation template"
