"""
The Meta Prompt Template. We can also have a bunch of differeent meta-prompt versions.
"""
from typing import Dict
    
from scai.modules.meta_prompt.models import MetaPrompt

META_PROMPT: Dict[str, MetaPrompt] = {
    "meta_prompt_1": MetaPrompt(
        name="meta_prompt_1",
        role="system",
        content="""Your job is to revise the system messsage of the assistant below to improve the conversation below.
        Conversation: {chat_history}""" 
    ),
}