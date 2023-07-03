"""
Assistant Prompt Template.
"""
from typing import Dict
    
from scai.assistant.models import AssistantPrompt

ASSISTANT_PROMPT: Dict[str, AssistantPrompt] = {
    "assistant_prompt_1": AssistantPrompt(
        id="assistant_prompt_1",
        name="helpful_assistant",
        role="system",
        content="""Instructions: {system_message}""",
    ),
}