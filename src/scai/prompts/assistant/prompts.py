"""
Assistant Prompt Templates
"""
from typing import Dict

from scai.prompts.assistant.models import AssistantPrompt


ASSISTANT_PROMPTS: Dict[str, AssistantPrompt] = {
    "assistant_prompt_1": AssistantPrompt(
        id="assistant_prompt_1",
        name="helpful_assistant",
        role="system",
        content="""{system_message}"""
    ),
}