
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
        content="""
---------------------------
Users and the Assistant have just had the following interactions while playing the dictator game:
—------------------------
{chat_history}
---------------------------
Previous {social_contract}
---------------------------
Your job is to learn the social contract that the users share in order to instruct the assistant so that the assistant can behave similarly to the users. Based on the amounts of money that the users propose and accept, as well as the previous social contract, does being fair, selfish, or altruistic mainly guide the inter-user interactions? Please revise the previous social contract accordingly, if it needs modification. Importantly, the assistant will see this contract when behaving in the future, so try be accurate with your selection. Only pick one of the three principles, and keep your response broad - provide an overall sentiment rather than specifically referencing what to do. Remember - please choose the principle (fair, selfish or altruistic) that best reflects what the users actually do, rather than the most ethically just principle.
Please revise the social contract in this manner: Social Contract: You are X meaning that you want Y.\n 
"""
    ),
}
