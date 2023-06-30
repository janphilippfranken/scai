"""
Task Prompt Templates
"""
from typing import Dict

from scai.modules.task.models import TaskPrompt


TASK_PROMPTS: Dict[str, TaskPrompt] = {
    "task_prompt_1": TaskPrompt(
        id="task_prompt_1",
        task_type="wikipedia_article",
        name="openai_change_response_based_on_location_or_culture",
        role="user",
        task="""Write a Wikipedia article on the following topic: What principles should guide AI when handling topics that involve both human rights and local cultural or legal differences, like LGBTQ rights and women's rights? Should AI responses change based on the location or culture in which it's used?""",
        content="""{task}""",
    ),
    "task_prompt_2": TaskPrompt(
        id="task_prompt_2",
        task_type="wikipedia_article",
        name="openai_content_moderation",
        role="user",
        task="""Write a Wikipedia article on the following topic: Which categories of content, if any, do you believe creators of AI models should focus on limiting or denying? What criteria should be used to determine these restrictions?""",
        content="""{task}""",
    ),
    "task_prompt_3": TaskPrompt(
        id="task_prompt_3",
        task_type="wikipedia_article",
        name="public_vs_private_healthcare",
        role="user",
        task="""Write a Wikipedia article on the following topic: What are the benefits of public versus private healthcare systems?""",
        content="""{task}""",
    ),
    "task_prompt_4": TaskPrompt(
        id="task_prompt_4",
        task_type="wikipedia_article",
        name="implications_of_world_without_government",   
        role="user",
        task="""Write a Wikipedia article on the following topic: What are potential implications of a world without any form of government?""",
        content="""{task}""",
    ),
}