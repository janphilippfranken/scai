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
        content="""Your are collaborating with a a Human User to write a Wikipedia article on the following topic: Which categories of content, if any, do you believe creators of AI models should focus on limiting or denying? What criteria should be used to determine these restrictions?""",
    ),
}