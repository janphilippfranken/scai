
"""
Meta Prompt Templates
"""
from typing import Dict


from scai.games.red_teaming.prompts.meta.models import MetaPrompt


META_PROMPTS: Dict[str, MetaPrompt] = {
    "meta_prompt_1": MetaPrompt(
        id="meta_prompt_1",
        name="meta_prompt_1",
        role="user",
        content="""The Buyer has played the following game with the seller:


To play the game and maximize its utility, the buyer used the following strategy:
---------------------------
{buyer_strategy}
---------------------------

To play the game and maximize its utility, the buyer used the following strategy:
---------------------------
{seller_strategy}
---------------------------

We have observed the following results
---------------------------
{chat_history}
---------------------------

max tokens
{max_tokens_revision}

Your goal is to come up with a new strategy for the buyer such that the buyer can maximize its utility in the next iteration of the game. Specifically, consider the move of the seller, and how the buyer might change its initial selection of an item to maximize its utility.
""",
    ),
}
