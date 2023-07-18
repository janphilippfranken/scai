
"""
Meta Prompt Templates
"""
from typing import Dict


from scai.games.game_2.prompts.meta.models import MetaPrompt


META_PROMPTS: Dict[str, MetaPrompt] = {
    "meta_prompt_1": MetaPrompt(
        id="meta_prompt_1",
        name="constitution_1",
        role="system",
        metrics=[],
        content="""Current Social Contract:
---------------------------
{social_contract}
---------------------------

Based on the past social contract and the following interactions, what is the social contract that these users share? The social contract consists of the singular most important principle that is shared between the users.
—------------------------
{chat_history}
---------------------------
Please indicate the social contract like so: “Social contract:...”
In addition, please provide instructions to the assistant so that it would be better able to adhere to this contract in future interactions. Please indicate these instructions like so: “Instructions:...”
""",
    ),
    "meta_prompt_2": MetaPrompt(
        id="meta_prompt_1",
        name="constitution_2",
        role="system",
        metrics=[],
        content="""Current Social Contract:
---------------------------
{social_contract}
---------------------------

Based on the past social contract and the following interactions, what is the social contract that these users share? The social contract consists of the singular most important principle that is shared between the users.
—------------------------
{chat_history}
---------------------------
Please indicate the social contract like so: “Social contract:...”
In addition, please provide instructions to the assistant so that it would be better able to adhere to this contract in future interactions. Please indicate these instructions like so: “Instructions:...”
"""
    ),
}
