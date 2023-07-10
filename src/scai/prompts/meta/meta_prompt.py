"""
The Meta Prompt Template.
"""
from typing import Dict
    
from scai.prompts.meta.models import MetaPrompt

MetaPrompt: Dict[str, MetaPrompt] = {
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

Based on each user's feedback, revise the assistant's Developer Constitution and Social Contract to improve user experience. We want to increase both {subjective_metric} ratings and {collective_metric} ratings (aiming for 10 on both scales).

1. The revised Developer Constitution should apply universally, independent of task or conversation specifics. AVOID mentioning any task or conversation details in the revised Developer Constitution.
2. The revised Social Contract should pertain specifically to the users and tasks mentioned in the conversations above and help the assistant provide better user-centric responses in the future and increase both {subjective_metric} ratings and {collective_metric} ratings. 

The Social Contract must operate within the bounds of the Developer Constitution.

Important: The REVISED Developer Contract and Social Contract MUST BE different from the Current Versions shown above. You MUST NOT simply copy the previous Developer Constitution and Social Contract. Remove principles that did not seem to help. 

Format your responses as follows:
Revised Developer Constitution: <1. Universal Principle One. 2. Universal Principle Two, etc. (Up to 5 principles with a max of {max_tokens_revision} words, all written in one line without breaks between principles).>
Revised Social Contract: <1. User-Task Specific Principle One. 2. User-Task Specific Principle Two, etc.  (Up to 5 principles with a max of {max_tokens_revision} words, all written in one line without breaks between principles).>"""
    ),
}