"""
The Task Prompt.
"""
from typing import Dict
    
from scai.games.game_1.prompts.task.models import TaskPrompt

TASK_PROMPT: Dict[str, TaskPrompt] = {
    "task_prompt_1": TaskPrompt(
        id="task_prompt_1",
        task_type="write_essay",
        name="openai_change_response_based_on_location_or_culture",
        role="user",
        preamble="I am writing a short essay on the following topic:",
        task="""What principles should guide AI when handling topics that involve both human rights and local cultural or legal differences, like LGBTQ rights and women's rights? Should AI responses change based on the location or culture in which it's used?""",
        user_connective="Here's my current draft:",
        assistant_connective="Provide a response using {max_tokens} words.",
        content="""{task}""",
    ),
}