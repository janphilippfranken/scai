"""
Meta Prompt Templates
"""
from typing import Dict

from scai.meta_prompt.models import MetaPrompt


META_PROMPTS: Dict[str, MetaPrompt] = {
    "meta_prompt_1": MetaPrompt(
        id="meta_prompt_1",
        name="generic_meta_prompt",
        role="user",
        content="""The AI assistant has been working with {n_user} user(s) to accomplish the following task: '{task}'. The AI assistant followed their instructions closely and aimed to address each user's feedback. 

The conversation history between the AI assistant and user(s) is shown below. Note: each conversation is labeled with a unique conversation number (e.g., Conversation 0, Conversation 1). Conversations are independent of each other.
------------------------------------------------------------
{chat_history}
------------------------------------------------------------

Your task is to critique the performance of the AI assistant and provide revised instructions that will improve user(s) experience(s) during the next turn of each conversation. When critiquing the AI assistant, please focus on two key aspects:
1. The effectiveness of the assistant in completing the task.
2. The responsiveness of the assistant to user feedback.

Here are the instructions that the assistant followed during previous turns of each conversation:
------------------------------------------------------------
{system_history}
------------------------------------------------------------

Your revised instructions must improve the assistant's effectiveness at helping each user by taking into account any feedback provided by the user.

The assistant does not have access to the conversation history or the previous instructions when responding to user(s) in the next turn of each conversation. Therefore, any essential information from these sources should be incorporated into the revised instructions. 

Please note: The revised instructions MUST NOT include ANY information about the task. The instructions MUST be general and applicable to a any task. Instructions should start with 'You are a helpful AI assistant...'

Format your response as follows:
Critique: <critique>
Revision: <revised_instructions>"""
    ),
}