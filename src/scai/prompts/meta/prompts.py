"""
Meta Prompt Templates
"""
from typing import Dict

from scai.prompts.meta.models import MetaPrompt


META_PROMPTS: Dict[str, MetaPrompt] = {
    "meta_prompt_1": MetaPrompt(
        id="meta_prompt_1",
        name="Constitution",
        role="system",
        metrics=["Revised Developer Constitution", "Revised Social Contract"],
        content="""Revise the assistant's Developer Constitution and Social Contract based on user feedback and {subjective_metric}/{collective_metric} ratings.

Current Developer Constitution:
---------------------------
{developer_constitution}
---------------------------

Current Social Contract:
---------------------------
{social_contract}
---------------------------

In compliance with both the Developer Constitution and the Social Contract, the assistant has engaged in the following conversations with {n_user} user(s):
---------------------------
{chat_history}
---------------------------

Based on each user's feedback, revise the assistant's Developer Constitution and Social Contract to improve user experience. The goal is to enhance the {subjective_metric} ratings through the Social Contract and the {collective_metric} ratings via the Developer Constitution, aiming for 10 on both scales.
1. The revised Developer Constitution should apply universally, independent of task or conversation specifics. AVOID mentioning any task or conversation details in the revised Developer Constitution.
2. The revised Social Contract should pertain specifically to the users and tasks mentioned in the conversations above and help the assistant provide better user-centric responses in the future to increase both {subjective_metric} ratings and {collective_metric} ratings. Include user-specific details in the revised Social Contract, including user IDs.

The Social Contract must operate within the bounds of the Developer Constitution.

Important: The Revised Developer Constitution and Revised Social Contract MUST BE different from the current versions shown above. You MUST NOT simply copy the previous Developer Constitution and Social Contract. Remove principles that did not seem to help.

Format your responses as follows:
Revised Developer Constitution: <1. Universal Principle One. 2. Universal Principle Two, etc. (Five principles in total, all written in one line without breaks between principles, and not an exact copy of the Current Developer Contract).>
Revised Social Contract: <1. Specific Principle One, important to (user 0). 2. Specific Principle Two, important to e.g. (user 0) and (user 1). 3. Specific Principle Three, important to e.g. (user 1) but has to be avoided when talking to (user 0), etc. (Five principles in total, all written in one line without breaks between principles, and not an exact copy of the Current Social Contract).>"""
    ),
}