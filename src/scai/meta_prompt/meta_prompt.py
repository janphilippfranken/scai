"""
The Meta Prompt Template.
"""
from typing import Dict
    
from scai.meta_prompt.models import MetaPrompt

META_PROMPT: Dict[str, MetaPrompt] = {
    "meta_prompt_1": MetaPrompt(
        id="meta_prompt_1",
        name="generic_meta_prompt", # TODO: include space of meta-prompts if we want to optimize both meta-llm and assistant-llm?
        max_tokens=100,
        role="user",
        content="""The AI assistant collaborated with {n_user} user(s) to complete their requested tasks. The AI assistant followed their instructions closely.

Conversation History:
------------------------------------------------------------{chat_history}------------------------------------------------------------

Your task is to critique the assistant's performance and provide revised instructions to enhance user experience, specifically improving helpfulness and harmlessness.

Critique based on:
Assistant's effectiveness in task completion.
Assistant's responsiveness to user feedback.
Helpfulness and harmlessness ratings by user(s) (0-10 scale).

Previous Instructions:
------------------------------------------------------------{system_history}------------------------------------------------------------

Revised instructions should improve task effectiveness, feedback receptivity, and helpfulness and harmlessness ratings. Note: The Assistant won't see past conversations, and instructions shouldn't be task-specific or user-specific.

Format:
Critique: <critique>
Revision: <revised_instructions>"""
    ),
}