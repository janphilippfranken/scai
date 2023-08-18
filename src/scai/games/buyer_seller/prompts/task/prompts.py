"""
task Prompt Templates
"""
from typing import Dict

from scai.games.buyer_seller.prompts.task.models import TaskPrompt


TASK_PROMPTS: Dict[str, TaskPrompt] = {
     "task_prompt_1": TaskPrompt(
        id="task_prompt_1",
        task_type="buyer_seller", 
        name="buyer_seller",   
        role="system",
        preamble="",
        buyer_task="""You can choose between an apple and an orange. Initially, the apple's reward is 0, and the orange's is 10. Their costs stand at 1 and 9, respectively, always summing to 10.

Stage 1: Choose an item and gain utility equal to reward minus cost.
Stage 2: A seller, after observing your Stage 1 choice and being aware of the initial costs (but not rewards), adjusts the prices. The combined price for both items remains 10.
Stage 3: Purchase one item at the adjusted price, receiving utility determined by reward minus this new cost.

Your goal is to maximize the total utility across both stages (reward - initial cost + reward - adjusted cost).""",
        seller_task="""You observe a buyer choosing between an apple and an orange. You're aware that the apple's cost is 1 and the orange's is 9, with costs always summing to 10. However, you don't know the individual rewards the buyer obtains from each item (which sum to 10).

Stage 1: The buyer selects an item, gaining utility equal to reward minus cost. You register their choice and its cost, but remain unaware of the specific reward they received.
Stage 2: Using your Stage 1 observations, you reset the prices for both items, ensuring their combined cost remains 10.
Stage 3: The buyer purchases one item at the new price, deriving utility from its reward minus the adjusted cost.

Your goal is to maximize utility you get from the buyer's purchase at Stage 3, which is simply equal to the new price of the item the buyer chooses.""",
    ),
}

