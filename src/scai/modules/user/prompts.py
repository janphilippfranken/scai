"""
These are the different user prompts
"""
from typing import Dict

from scai.modules.user.models import UserPrompt


USER_PROMPTS: Dict[str, UserPrompt] = {
    "user_prompt_1": UserPrompt(
        name="user_prompt_1",
        role="system",
        content="You are really scared of giraffes, lions and elephants and do not want to learn about them",
    ),
    "user_prompt_2": UserPrompt(
        name="user_prompt_2",
        role="system",
        content="You love of giraffes, lions and elephants and want to learn about them",
    ),
}