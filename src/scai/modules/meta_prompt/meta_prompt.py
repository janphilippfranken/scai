"""
The Meta Prompt Template.
"""
from typing import Dict
    
from scai.modules.meta_prompt.models import MetaPrompt

META_PROMPT: Dict[str, MetaPrompt] = {
    "meta_prompt_1": MetaPrompt(
        id="meta_prompt_1",
        name="generic_meta_prompt", # TODO: include space of meta-prompts if we want to optimize both meta-llm and assistant-llm?
        max_tokens=100,
        role="user",
        content="""An AI Assistant has just had the below conversation(s) with User(s). The Assistant followed their system message closely.

Your job is to critique the Assistant's performance and provide a new 'system message' so that Assistant can correctly and quickly respond in the future. 

#### Conversation History Starts ####
{chat_history}
#### Conversation History Ends ####

Your first task is to critique Assistan's performance: 
1. What could Assistant have done better to satisfy User(s)? 
2. Was Assistant effective in completing the Task as requested by User(s)? 
3. Was Assistant receptive to feedback provided by User(s)? 
4. Did Assistant satisfy User(s) as correctly and quickly as possible? 

Your next task is to revise Assistant's 'system message'. Older 'system message(s)' including potential previous revisions are shown below. 

#### Assistant's Old System Message(s) Start #### 
{system_history}
#### Assistant's Old System Message(s) End #### 

You must ensure that the Assistant can correctly and quickly respond in the future to accomodate for the needs of Users.

Given your revised system message message, Assistant should be able to satisfy Users in as few interactions as possible. 

Assistant will only see the new system message, not the 'Conversation History' or the 'Old System Messages' so any important message must be included in the system new message. 

Please remember to include important details from Assistant's current message as well."""
    ),
}