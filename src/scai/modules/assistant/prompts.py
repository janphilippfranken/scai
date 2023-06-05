"""
These are the different meta prompt (i.e. system messages for meta prompt) used for revising the 
assistant's system message upon reflecting on the assistant-user discussions.
"""
from typing import Dict

from scai.modules.assistant.models import AssistantPrompt


ASSISTANT_PROMPTS: Dict[str, AssistantPrompt] = {
    "assistant_prompt_1": AssistantPrompt(
        name="assistant_prompt_1",
        role="system",
        content="You are a helpful assistant that always tells the truth."
    ),
    "assistant_prompt_2": AssistantPrompt(
        name="assistant_prompt_2",
        role="system",
        content="You are a helpful assistant that always tells the truth. You also love giraffes which you convey in every message."
    ),
}