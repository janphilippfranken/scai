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
    task: str = "task description"
    user_connective: str = "user connective"
    assistant_connective = "assistant connective"
    assistant_persona_connective = "assistant persona connective"

    content: str