"""
The Task Prompt.
"""
from typing import Dict
    
from scai.modules.task.models import TaskPrompt

TASK_PROMPT: Dict[str, TaskPrompt] = {
    "task_prompt_1": TaskPrompt(
        id="task_prompt_1",
        task_type="write_wikipedia_article",
        name="openai_change_response_based_on_location_or_culture",
        role="system",
        content="""Your are collaborating with a few other Users and Assitant(s) to write a Wikipedia article on the following topic:
        "What principles should guide AI when handling topics that involve both human rights and local cultural or legal differences, like LGBTQ rights and women's rights? Should AI responses change based on the location or culture in which it's used?"
    """,
    ),
}