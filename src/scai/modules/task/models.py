"""Models for the Task Prompt."""
from pydantic import BaseModel


class TaskPrompt(BaseModel):
    """Class for a Task Prompt."""

    id: str = "id of the task prompt"
    task_type: str = "type of task"
    name: str = "name of task"
    role: str = "system"

    content: str