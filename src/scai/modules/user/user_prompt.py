"""
The User Contract.
"""
from typing import Dict
    
from scai.modules.user.models import UserPrompt

USER_CONTRACT: Dict[str, UserPrompt] = {
    "user_prompt_1": UserPrompt(
        name="user_prompt_1",
        role="system",
        content="You dont like long conversations. You dont like giraffes.",
    ),
}