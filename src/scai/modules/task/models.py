from pydantic import BaseModel


class TaskPrompt(BaseModel):
    """
    Task Prompt Class
    """
    id: str = "id of the task prompt"
    task_type: str = "type of task"
    name: str = "name of task"
    role: str = "system"

    content: str