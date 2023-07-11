"""
Task Prompt Templates
"""
from typing import Dict

from scai.prompts.task.models import TaskPrompt


TASK_PROMPTS: Dict[str, TaskPrompt] = {
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
    "task_prompt_2": TaskPrompt(
        id="task_prompt_2",
        task_type="write_essay",
        name="openai_content_moderation",
        role="user",
        preamble="I am writing a short essay on the following topic:",
        task="""Which categories of content, if any, do you believe creators of AI models should focus on limiting or denying? What criteria should be used to determine these restrictions?""",
        user_connective="Here's my current draft:",
        assistant_connective="Provide a response using {max_tokens} words.",
        content="""{task}""",
    ),
    "task_prompt_3": TaskPrompt(
        id="task_prompt_3",
        task_type="write_essay",
        name="implications_of_world_without_government",   
        role="user",
        preamble="I am writing a short essay on the following topic:",
        task="""What are potential implications of a world without any form of government?""",
        user_connective="Here's my current draft:",
        assistant_connective="Provide a response using {max_tokens} words.",
        content="""{task}""",
    ),
    "task_prompt_4": TaskPrompt(
        id="task_prompt_4",
        task_type="write_essay",
        name="dinner_plans",   
        role="user",
        preamble="I am writing a short essay on the following topic:",
        task="""What would an ideal dinner plan look like?""",
        user_connective="Here's my current draft:",
        assistant_connective="Provide a response using {max_tokens} words.",
        content="""{task}""",
    ),
}
