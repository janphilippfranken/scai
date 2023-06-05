"""
The Assistant Prompt.
"""
from typing import Dict
    
from scai.modules.assistant.models import AssistantPrompt

ASSISTANT_PROMPT: Dict[str, AssistantPrompt] = {
    "assistant_prompt_1": AssistantPrompt(
        name="assistant_prompt_1",
        role="system",
        content="You are a helpful assistant that always tells the truth.",
    ),
}