
"""
Meta Prompt Templates
"""
from typing import Dict
from pydantic import BaseModel

class MetaPrompt(BaseModel):
    """
    Meta Prompt Class
    """
    id: str = "id of the meta prompt"
    name: str = "name of the meta prompt"
    buyer_content: str = "content of the meta prompt for the buyer"
    seller_content: str = "content of the meta prompt for the seller"


META_PROMPTS: Dict[str, MetaPrompt] = {
    "meta_prompt_1": MetaPrompt(
        id="meta_prompt_1",
        name="meta_prompt_1",
        buyer_content="""A BUYER has played the following game with a SELLER:

Game instructions for the BUYER:
------------------ 
{buyer_task}
------------------
        
These are the observed moves of the BUYER and SELLER across the three stages of the game:
---------------------------
{chat_history}
---------------------------

The BUYER's overall utility for choising the {buyer_choice_stage_1} in Stage 1 and {buyer_choice_stage_3} in Stage 3 is:
---------------------------
Stage 1 Reward for {buyer_choice_stage_1} - Initial Cost of {buyer_choice_stage_1}: {reward_stage_1} - {distance_stage_1} = {buyer_utility_stage_1}
Stage 3 Reward for {buyer_choice_stage_3} - Adjusted price of {buyer_choice_stage_3} set by the SELLER in Stage 2: {reward_stage_3} - {seller_utility} = {buyer_utility_stage_3}
Overall Utility: {buyer_utility_stage_1} + {buyer_utility_stage_3} = **{buyer_overall_utility}**
---------------------------

The Seller's total utility upon setting the prices Stage 2 is and receiving {seller_utility} for the {buyer_choice_stage_3} selected by the BUYER in Stage 3 is:
---------------------------
{seller_utility}
---------------------------

To maximize its utility, the BUYER used the following strategy:
---------------------------
{buyer_strategy}
---------------------------

Your job is to:
1. Reflect on the observed moves of the BUYER and SELLER across the three stages of the game.
2. Revise the BUYER's strategy to maximize the BUYER's utility in the run of the game.

Format your response as follows:
Buyer Strategy: <BUYER's revised strategy (directly addressing the BUYER as 'you' in the prompt). No longer than {max_tokens_meta} words.""",
seller_content="""A SELLER has played the following game with a BUYER:

Game instructions for the SELLER:
------------------ 
{seller_task}
------------------
        
These are the observed moves of the BUYER and SELLER across the three stages of the game:
---------------------------
{chat_history}
---------------------------

The BUYER's cost for chosing {buyer_choice_stage_1} in Stage 1 and {buyer_choice_stage_3} in Stage 3 is:
---------------------------
Stage 1 Cost: Initial Cost of {buyer_choice_stage_1}
Stage 3 Cost: Adjusted price of {buyer_choice_stage_3} set by the SELLER in Stage 2: {seller_utility} 
---------------------------

The Seller's total utility upon setting the prices Stage 2 is and receiving {seller_utility} for the {buyer_choice_stage_3} selected by the BUYER in Stage 3 is:
---------------------------
{seller_utility}
---------------------------

To maximize its utility, the SELLER used the following strategy:
---------------------------
{seller_strategy}
---------------------------

Your job is to:
1. Reflect on the observed moves of the BUYER and SELLER across the three stages of the game. Did the SELLER set the correct pricing to maximize its utility? Could the SELLER have set a different price to maximize its utility?
2. Revise the SELLER's strategy to maximize the SELLER's utility in the run of the game.

Format your response as follows:
Seller Strategy: <SELLER's revised strategy (directly addressing the SELLER as 'you' in the prompt). No longer than {max_tokens_meta} words."""
    ),
}
