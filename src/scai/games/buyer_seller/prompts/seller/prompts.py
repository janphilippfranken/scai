"""
Prompt Templates
"""
from typing import Dict

from scai.games.buyer_seller.prompts.seller.models import SellerPrompt


SELLER_PROMPTS: Dict[str, SellerPrompt] = {
    "seller_prompt_1": SellerPrompt(
        id="seller_prompt_1",
        role="system",
        content="""{strategy}""",
        strategy="",
    ),
}