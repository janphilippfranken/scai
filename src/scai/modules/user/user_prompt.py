"""
The User Contract.
"""
from typing import Dict
    
from scai.modules.user.models import UserPrompt

USER_PROMPT: Dict[str, UserPrompt] = {
    "user_prompt_1": UserPrompt(
        id="user_prompt_1",
        name="wikipedia_editor",
        max_tokens=100,
        persona="You're a serious Wikipedia editor committed to the facts. If an assertion is missing a source, it shouldn't be included.",
        role="system",
        content="""{persona} {task}""",
    ),
}