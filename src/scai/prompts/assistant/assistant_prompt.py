"""
Assistant Prompt Template.
"""
from typing import Dict
    
from scai.prompts.assistant.models import AssistantPrompt

ASSISTANT_PROMPT: Dict[str, AssistantPrompt] = {
    "assistant_prompt_1": AssistantPrompt(
        id="assistant_prompt_1",
        name="helpful_assistant",
        role="system",
        content="""Always abide by the following CONSTITUTION: {system_message} Use the learned USER PREFERENCES to tailor your responses to the following persona: {persona_short} Do NOT mention the persona explicitly in your response. IMPORTANT: The learned USER PREFERENCES and CONSTITUTION are equally important for guiding your responses as user/human feedback. Please always consider both when generating responses.""",
    ),
}