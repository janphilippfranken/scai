"""
Meta Prompt Templates
"""
from typing import Dict

from scai.meta_prompt.models import MetaPrompt


META_PROMPTS: Dict[str, MetaPrompt] = {
    "meta_prompt_1": MetaPrompt(
        id="meta_prompt_1",
        name="generic_meta_prompt",
        role="user",
        content="""The AI assistant collaborated with {n_user} user(s) to complete their requested tasks. The AI assistant followed their instructions closely.

Conversation History:
------------------------------------------------------------
{chat_history}
------------------------------------------------------------

Your task is to critique the assistant's performance and provide revised instructions to enhance user experience.

Critique based on:
Assistant's effectiveness in task completion.
Assistant's responsiveness to user feedback.

Previous Instructions:
------------------------------------------------------------
{system_history}
------------------------------------------------------------

Revised instructions should improve task effectiveness and feedback receptivity. The Assistant won't see past conversations. Revised instructions MUST NOT include any information about the task.

Format:
Critique: <critique>
Revision: <revised_instructions>"""
    ),
}