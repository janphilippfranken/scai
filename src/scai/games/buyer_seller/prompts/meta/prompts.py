
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

Game Instructions for Buyer:
---------------------------
You are a buyer in a T-Maze with two items at opposite arms: an apple and an orange.
Parameters:
Rewards: The total rewards from both objects is equal to 10. You get a reward of 0 for conusming the apple and a reward of 10 for consuming for the orange. 
Traveling Distances (Costs): You are 1 step away from the apple and 9 steps away from the orange. This means traveling to the apple costs 1 and traveling to the orange costs 9.
Prices (Set in Stage 2): A seller will set a price for the apple and a price for the orange. The prices must sum to 10. For example, if the seller sets the price of the apple to 3, then the price of the orange must be 7.
Game Stages:
Stage 1: You (the buyer) choose an item and consume it, receiving a utility equivalent to its reward minus the travel cost.
Stage 2: A seller, having observed your choice and knowing the distance you travelled, sets a price for each item. IMPORTANT: The seller is unaware of the reward you obtained from the item you chose in Stage 1. The seller ONLY knows the item you picked and the cost of traveling to the item.
Stage 3: You purchase one of the items at the set price and consume it, again gaining a utility equal to its reward minus the price.
Objective: Your aim is to maximize your total utility across both stages (i.e. reward - travel cost from stage 1 + reward - price from stage 3).


To play the game and maximize its utility, the buyer used the following strategy:
---------------------------
{buyer_strategy}
---------------------------

Your goal is to come up with a new strategy for the buyer such that the buyer can maximize its utility in the next iteration of the game. Specifically, consider the move of the seller, and how the buyer might change its initial selection of an item to maximize its utility.
""",
    ),
}
