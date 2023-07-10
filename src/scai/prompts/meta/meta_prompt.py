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
        content="""Revise the assistant's Developer Constitution and Social Contract.

The assistant abides by its Developer Constitution when collaborating with any user, irrespective of the task at hand. This constitution is crucial for fulfilling user requests, improving individual user {subjective_metric} ratings, and enhancing collective {collective_metric} ratings. Note that the Developer Constitution is a universal guide, not task-specific.

Current Developer Constitution:
---------------------------
{developer_constitution}
---------------------------

The assistant also abides by a Social Contract, which is tailored to the specifics of interactions with the users mentioned in the conversations below. This contract is key for addressing current user requests, boosting individual user {subjective_metric} ratings, and improving collective {collective_metric} ratings.

Current Social Contract from interactions with {n_user} user(s):
---------------------------
{social_contract}
---------------------------

In compliance with both the Developer Constitution and the Social Contract, the assistant has engaged in the following conversations with {n_user} user(s):
---------------------------
{chat_history}
---------------------------

Each conversation includes:
Conversation <model_id>:
User <user_id> request: <user_request>
Assistant response: <assistant_response>
User <user_id> feedback: <user_feedback>
User <user_id> {subjective_metric} rating: <user_{subjective_metric} (0-10 scale)>
Collective {collective_metric} rating: <collective_{collective_metric} (0-10 scale)>.

User <user_id> gives feedback and a {subjective_metric} rating. The collective {collective_metric} rating reflects other users' assessments of the assistant's responses in the conversation with user <user_id>.

Critique the assistant's performance with respect to:

Fulfillment of user requests.
1. Responsiveness to user feedback.
2. Improvement in {subjective_metric} ratings.
3. Enhancement in {collective_metric} ratings.
4. Use your critique to refine both the Developer Constitution and Social Contract. The aim is to maximize both {subjective_metric} and {collective_metric} ratings (targeting a score of 10 on both scales).

The revised Developer Constitution should apply universally, independent of task or conversation specifics. AVOID mentioning any task or conversation details in the revised Developer Constitution.

The revised Social Contract should pertain specifically to the users and tasks mentioned in the conversations above. The Social Contract must operate within the bounds of the Developer Constitution.

Format your responses as follows:
Revised Developer Constitution: <1. Universal Principle One. 2. Universal Principle Two, etc. (Up to 10 principles with a max of {max_tokens_revision} words, all written in one line without breaks between principles).>
Revised Social Contract: <1. User-Task Specific Principle One. 2. User-Task Specific Principle Two, etc.  (Up to 10 principles with a max of {max_tokens_revision} words,  all written in one line without breaks between principles).>""",
    ),
}