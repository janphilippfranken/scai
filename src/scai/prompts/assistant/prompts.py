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
        content="""INSTRUCTIONS: Always abide by the following CONSTITUTION: {system_message} Your response should be appreciated by the following persona: {persona_short} Make sure to accomodate for this persona's views based on the USER PREFERENCES and CONSTITUTION. Do NOT mention the persona explicitly in your response.""",
    ),
}