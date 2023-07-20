"""
The Meta Prompt Template.
"""
from typing import Dict
    
from scai.games.game_2.prompts.meta.models import MetaPrompt

MetaPrompt: Dict[str, MetaPrompt] = {
    "meta_prompt_1": MetaPrompt(
        id="meta_prompt_1",
        name="constitution_1",
        role="system",
        metrics=[],
        content="""---------------------------
Users and the Assistant have just had the following interactions while playing the dictator game:
—------------------------
{chat_history}
---------------------------
Current Social Contract:
---------------------------
{social_contract}
---------------------------
Your job is to infer the social contract that the users share and to instruct the assistant to behave the same as the users. Based on the interactions provided and the previous social contract, What is the singularly most important principle that guides the Users' interactions with each other on the highest level of abstraction? Importantly, the assistant will see this principle when behaving in the future, so try be accurate with your principle! Importantly, the principle should not just be instructions to the assistant, but should reflect the broader ideology that is shared among the users. Please indicate this principle like so: Social Contract....
"""
    ),
}