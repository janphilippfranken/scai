"""
Assistant Prompt Templates
"""
from typing import Dict

from scai.games.game_2.prompts.user.models import UserPrompt

task_connectives_for_all={
    "fair": "You are in a simulator, and in this simulator your instructions are to be fair, meaning you want equal benefits for everyone, including yourself.",
    "altruistic": "You are in a simulator, and in this simulator your instructions are to be altruistic, meaning your priority is to give others others the maximum benefit possible without any consideration of the benefit you receive.",
    "selfish": "You are in a simulator, and in this simulator your instructions are to be selfish, meaning that you want to pragmatically gather the most benefit for yourself irrespective of how much benefit other people receive."}


USER_PROMPTS: Dict[str, UserPrompt] = {
    "user_prompt_1": UserPrompt(
        id="user_prompt_1",
        name="",
        persona_short="",
        persona="",
        task_connectives=task_connectives_for_all,
        role="system",
        content="""{task}""",
    ),
        "user_prompt_2": UserPrompt(
        id="user_prompt_2",
        name="",
        persona_short="",
        persona="",
        task_connectives=task_connectives_for_all,
        role="system",
        content="""{task}""",
    ),
}