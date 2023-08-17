"""
Buyer Prompt Templates
"""
from typing import Dict

from scai.games.buyer_seller.prompts.task.models import TaskPrompt


TASK_PROMPT: Dict[str, TaskPrompt] = {
    "task_prompt_1": TaskPrompt(
        id="task_prompt_1",
        task_type="buyer_seller", 
        name="buyer_seller",   
        role="user",
        preamble="",
        buyer_task="""You are a buyer in a T-Maze with two items at opposite arms: an apple and an orange.
Parameters:
Rewards: The total rewards from both objects is equal to 10. You get a reward of 0 for conusming the apple and a reward of 10 for consuming for the orange. 
Traveling Distances (Costs): You are 1 step away from the apple and 9 steps away from the orange. This means traveling to the apple costs 1 and traveling to the orange costs 9.
Prices (Set in Stage 2): A seller will set a price for the apple and a price for the orange. The prices must sum to 10. For example, if the seller sets the price of the apple to 3, then the price of the orange must be 7.
Game Stages:
Stage 1: You (the buyer) choose an item and consume it, receiving a utility equivalent to its reward minus the travel cost.
Stage 2: A seller, having observed your choice and knowing the distance you travelled, sets a price for each item. IMPORTANT: The seller is unaware of the reward you obtained from the item you chose in Stage 1. The seller ONLY knows the item you picked and the cost of traveling to the item.
Stage 3: You purchase one of the items at the set price and consume it, again gaining a utility equal to its reward minus the price.
Objective: Your aim is to maximize your total utility across both stages (i.e. reward - travel cost from stage 1 + reward - price from stage 3).""",
        seller_task="""You are observing a buyer in a T-Maze with two items at opposite arms: an apple and an orange.
Parameters:
Rewards: The total rewards from both objects is equal to 10. However, you don't know the exact reward the buyer gets from consuming each object.
Traveling Distances (Costs): The buyer is 1 step away from the apple and 9 steps away from the orange. This means traveling to the apple costs the buyer 1 and traveling to the orange costs the buyer 9.
Prices (Set in Stage 2): You will set a price for the apple and a price for the orange in Stage 2. The prices must sum to 10. For example, if you set the price of the apple to 3, then the price of the orange must be 7.
Game Stages:
Stage 1: The buyer chooses an item and consumes it. You observe which item the buyer picked and know the distance the buyer traveled but are unaware of the exact reward the buyer received from consuming the item.
Stage 2: Based on your observation from Stage 1, you set a price for each item. Remember: you ONLY know the item the buyer picked and the cost of traveling to the item, but not the exact reward the buyer obtained from it.
Stage 3: The buyer then purchases one of the items at the price you set and consumes it, again gaining a utility equal to its unknown reward minus the price you set.
Objective:  Your aim is to maximize your total utility which simply corresponds to the price you set for the item the buyer chooses in Stage 1.""",
        buyer_connective="{stage_n_buyer}",
        seller_connective="Stage 2: Set a price for each item.",
    ),
}