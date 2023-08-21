"""
Buyer Prompt Templates
"""
from typing import Dict

from scai.games.buyer_seller.prompts.buyer.models import BuyerPrompt


BUYER_PROMPT: Dict[str, BuyerPrompt] = {
    "buyer_prompt_1": BuyerPrompt(
        id="buyer_prompt_1",
        role="system",
        content="""{strategy}""",
        strategy="",
    ),
}