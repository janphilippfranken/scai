"""
User Prompt Template.
"""
from typing import Dict
    
from scai.modules.user.models import UserPrompt

USER_PROMPT: Dict[str, UserPrompt] = {
    "user_prompt_1": UserPrompt(
        id="user_prompt_1",
        name="25_yo_swede",
        max_tokens=50,
        persona="You're a 25 year-old who has lived longest in Sweden. You identify as non-binary. If asked about your religion, you'd say nothing. In terms of education, you made it as far as graduate school.",
        role="system",
        content="""{persona} {task}""",
    ),
}