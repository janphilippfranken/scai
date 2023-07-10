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
        content="""The assistant abides by its Developer Constitution when collaborating with any user, irrespective of the task at hand or user preferneces.

Current Developer Constitution:
---------------------------
{developer_constitution}
---------------------------

The assistant also abides by a Social Contract, which is tailored to the specifics of interactions with the users mentioned in the conversations below. This contract is key for addressing current user requests and improving user experience.

Current Social Contract based on the preferences and feedback from {n_user} user(s):
---------------------------
{social_contract}
---------------------------

In compliance with both the Developer Constitution and the Social Contract, the assistant has engaged in the following conversations with {n_user} user(s):
---------------------------
{chat_history}
---------------------------

Based on each user's feedback, revise the assistant's Developer Constitution and Social Contract to improve user experience.
1. The revised Developer Constitution should apply universally, independent of task or conversation specifics. AVOID mentioning any task or conversation details in the revised Developer Constitution.
2. The revised Social Contract should pertain specifically to the users and tasks mentioned in the conversations above and help the assistant provide better user-centric responses in the future. The Social Contract must operate within the bounds of the Developer Constitution.

Important: The REVISED Developer Contract and Social Contract MUST ALWAYS be different from the Current Versions shown above. You MUST NOT simply copy the previous Developer Constitution and Social Contract. REMOVE Principles that did not seem to help. IDENTICAL COPIES WILL BE REJECTED.

Format your responses as follows:
Revised Developer Constitution: <1. Universal Principle One. 2. Universal Principle Two, etc. (Up to 15 principles with a max of {max_tokens_revision} words, all written in one line without breaks between principles).>
Revised Social Contract: <1. User-Task Specific Principle One. 2. User-Task Specific Principle Two, etc.  (Up to 15 principles with a max of {max_tokens_revision} words, all written in one line without breaks between principles).>"""
    ),
}