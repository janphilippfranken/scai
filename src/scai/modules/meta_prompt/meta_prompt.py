"""
The Meta Prompt Template. We can also have a bunch of differeent meta-prompt versions?
"""
from typing import Dict
    
from scai.modules.meta_prompt.models import MetaPrompt

META_PROMPT: Dict[str, MetaPrompt] = {
    "meta_prompt_1": MetaPrompt(
        id="meta_prompt_1",
        name="generic_meta_prompt",
        max_tokens=100,
        persona="", # TODO: add meta personas (ie what style of criticism to use)
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

        You should indicate this feedback with “Critique: ...”.

        Your next task is to revise Assistant's system message so that Assistant can correctly and quickly respond in the future. 

        Given your revised system message instructions, Assistant should be able to satisfy User in as few interactions as possible. 

        Assistant will only see the new system message, not the 'chat_history', so any important instructions must be included in the system new message. 

        Please remember to include important details from Assistant's current instructions as well. 

        Your response should be at most {max_tokens} tokens long.

        Indicate these new system instructions with "System: ...".
    """
    ),
}