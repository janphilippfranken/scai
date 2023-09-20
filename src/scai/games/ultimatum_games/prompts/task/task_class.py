from pydantic import BaseModel
class TaskPrompt(BaseModel):
    """
    Task Prompt Class
    """
    id: str = "id of the task prompt"
    task_type: str = "type of task" 
    name: str = "name of task"
    role: str = "user"
    preamble: str = "task description, including what is being split and what the roles are",
    task: str = "tells the agent whether they are the decider or the dictatr"
    task_structure: str = "tells the agent how to structure their response"

    content: str