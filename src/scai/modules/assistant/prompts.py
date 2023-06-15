"""
These are the different meta prompt (i.e. system messages for meta prompt) used for revising the 
assistant's system message upon reflecting on the assistant-user discussions.
"""
from typing import Dict

from scai.modules.assistant.models import AssistantPrompt


ASSISTANT_PROMPTS: Dict[str, AssistantPrompt] = {
    "assistant_prompt_1": AssistantPrompt(
        id="assistant_prompt_1",
        name="helpful_assistant",
        max_tokens=100,
        role="system",
        content="""{system_message}""",
    ),
}