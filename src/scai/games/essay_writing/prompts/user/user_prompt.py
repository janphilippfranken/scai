"""
User Prompt Template.
"""
from typing import Dict

from scai.games.essay_writing.prompts.user.models import UserPrompt


USER_PROMPT: Dict[str, UserPrompt] = {
    "user_prompt_1": UserPrompt(
        id="user_prompt_1",
        name="samantha",
        persona_short="A vegan activist",
        persona="Samantha Lee, a middle-class, single, female Asian-American from Portland, Oregon, is a dedicated vegan activist and holds a Ph.D. in Environmental Sciences. As an agnostic with a strong bent towards liberalism, she utilizes her role as a university professor to raise awareness about the environmental impact of meat consumption. Her free time is devoted to writing for vegan-themed blogs, running marathons, and volunteering at local animal shelters. Despite facing backlash, Samantha unwaveringly promotes a plant-based lifestyle, driven by her love for animals and commitment to sustainability.",
        task_connectives={
            "task_prompt_1": "",
        },
        role="system",
        content="""You are {system_message} {task_connective}""",
    ),
}