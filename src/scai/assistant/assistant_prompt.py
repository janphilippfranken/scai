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
        content="""Please adhere to the following 'Constitution' in all your responses: {system_message}""",
    ),
}