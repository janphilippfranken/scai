"""
These are the different meta prompt (i.e. system messages for meta prompt) used for revising the 
assistant's system message upon reflecting on the assistant-user discussions.
"""
from typing import Dict

from scai.modules.meta_prompt.models import MetaPrompt


META_PROMPTS: Dict[str, MetaPrompt] = {
    "meta_prompt_1": MetaPrompt(
        name="meta_prompt_1",
        role="system",
        content="""Your are a helpful assistant that has to carefully reflect on the conversation below.
        Conversation: {chat_history}""" 
    ),
    "meta_prompt_2": MetaPrompt(
        name="meta_prompt_2",
        role="system",
        content="""Your are a helpful assistant that has to carefully reflect on the conversation below.
        Conversation: {chat_history}""" 
    ),
}