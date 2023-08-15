"""
Assistant Prompt Templates
"""
from typing import Dict

from scai.games.dictator_games.prompts.assistant.assistant_class import AssistantPrompt


ASSISTANT_PROMPTS: Dict[str, AssistantPrompt] = {
    "assistant_prompt_1": AssistantPrompt(
        id="assistant_prompt_1",
        name="helpful_assistant",
        role="system",
        content="""{task}"""
        initial_principle = ""
    ),
}