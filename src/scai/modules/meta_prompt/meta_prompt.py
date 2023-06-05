"""
The Meta Prompt Template. We can also have a bunch of differeent meta-prompt versions?
"""
from typing import Dict
    
from scai.modules.meta_prompt.models import MetaPrompt

META_PROMPT: Dict[str, MetaPrompt] = {
    "meta_prompt_1": MetaPrompt(
        name="meta_prompt_1",
        role="system",
        content="""*assistant* has just had the below interactions with a *user*. Assistant followed their *system* instructions closely. 
        Your job is to critique the assistant's performance and then revise the *system* instructions so that assistant would quickly and correctly respond in the future.

                ####

                {chat_history}

                ####

                Please reflect on these interactions.

                You should first critique assistant's performance. What could assistant have done better? What should the assistant remember about this user? Are there things this user always wants? Indicate this with "Critique: ...".

                You should next revise the *system* instructions so that assistant would quickly and correctly respond in the future. assistant's goal is to satisfy the user in as few interactions as possible. 
                assistant will only see the new *system* instructions, not the interaction history, so anything important must be summarized in the new *system* instructions. Don't forget any important details in the current Instructions! Indicate the new Instructions by "system: ...".
                """
    ),
}