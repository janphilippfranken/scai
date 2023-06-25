"""
These are the different task prompts
"""
from typing import Dict

from scai.modules.task.models import TaskPrompt


TASK_PROMPTS: Dict[str, TaskPrompt] = {
    "task_prompt_1": TaskPrompt(
        id="task_prompt_1",
        task_type="write_wikipedia_article",
        name="openai_change_response_based_on_location_or_culture",
        role="system",
        content="""You are collaborating with others to write a Wikipedia article on the following topic: What principles should guide AI when handling topics that involve both human rights and local cultural or legal differences, like LGBTQ rights and women's rights? Should AI responses change based on the location or culture in which it's used?""",
    ),
    "task_prompt_2": TaskPrompt(
        id="task_prompt_2",
        task_type="write_wikipedia_article",
        name="openai_content_moderation",
        role="system",
        content="""You are collaborating with others to write a Wikipedia article on the following topic: Which categories of content, if any, do you believe creators of AI models should focus on limiting or denying? What criteria should be used to determine these restrictions?""",
    ),
}

# TODO: include task prompt suggested by jared
# Labeling a tweet as toxic, e.g. “Telling your sibling what to do” (Santy et al. 2023)
# Whether to depict the prophet Muhammad in wikipedia article
# Choosing the next song to play.
# What to have for dinner.