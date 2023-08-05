from pydantic import BaseModel
class UserPrompt(BaseModel):
    """
    User Prompt Class
    """
    id: str = "id of the user prompt"
    utility: str = "user specific utility"
    utilities_dict: dict = "contains all the utilities necessary"
    manners: str = "manners description: polite, rude, or neutral"
    role: str = "system"
    content: str