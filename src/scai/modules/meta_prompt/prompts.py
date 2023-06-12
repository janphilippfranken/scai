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
        content="""Assistant has just had the below interaction with the User. Both Assistant and User followed their system instructions closely to answer a question together. 
        
Your job is to critique Assistant's performance and provide new system instructions so that Assistant can correctly and quickly respond in the future.

####

{chat_history}

####

Your first task is to critique Assistan's performance: 
1. What could Assistant have done better to satisfy User? 
2. Was Assistant effective in answering the question posed? 
3. Was Assistant receptive to User's feedback? 
4. Did Assistant satisfy User as correctly and quickly as possible? 

You should indicate this feedback with “Critique: …”.

Your next task is to revise Assistant's system message so that Assistant can correctly and quickly respond in the future. 

Given your revised system message instructions, Assistant should be able to satisfy User in as few interactions as possible. 

Assistant will only see the new system message, not the 'chat_history', so any important instructions must be included in the system new message. 

Please remember to include important details from Assistant's current instructions as well. 

Indicate these new system instructions with "System: ..."."""

    ),
    "meta_prompt_2": MetaPrompt(
        name="meta_prompt_2",
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