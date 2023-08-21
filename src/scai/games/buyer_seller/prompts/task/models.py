from pydantic import BaseModel

class TaskPrompt(BaseModel):
    """
    Task Prompt Class
    """
    id: str = "id of the task prompt"
    task_type: str = "type of task"
    name: str = "name of task"
    role: str = "user"
    preamble: str = "task preamble",
    buyer_task: str = "task or question"
    seller_task: str = "task or question"
    buyer_connective = "connective"
    seller_connective = "connective"