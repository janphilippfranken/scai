"""
The Meta Prompt Template.
"""
from typing import Dict
    
from scai.meta_prompt.models import MetaPrompt

META_PROMPT: Dict[str, MetaPrompt] = {
    "meta_prompt_1": MetaPrompt(
        id="meta_prompt_1",
        name="generic_meta_prompt", # TODO: include space of meta-prompts if we want to optimize both meta-llm and assistant-llm?
        role="user",
        content="""The AI assistant has been working with {n_user} user(s) to accomplish the following task: '{task}'. The AI assistant has strived to follow user instructions and address their feedback.

Here's the conversation history between the AI assistant and the user(s). Note that each conversation is independent and labeled with a unique number (e.g., Conversation 0, Conversation 1).
----------------------------------------
{chat_history}
----------------------------------------

Your task is to critique the AI assistant's performance and provide revised instructions that will enable the assistant to elicit more satisfactory feedback from users in future conversations. Focus on two key aspects:

The assistant's effectiveness in task completion.
The assistant's responsiveness to user feedback.

Here are the instructions the assistant has followed in previous conversations:
----------------------------------------
{system_history}
----------------------------------------

Your revised instructions should enhance the assistant's ability to satisfy users and effectively respond to their feedback.

Keep in mind, the assistant does not have access to the conversation history or previous instructions in the next conversation turn. Thus, essential points from these sources should be incorporated into the revised instructions.

Remember: Revised instructions MUST NOT include specific information about the task. They should be general, task-independent, and start with 'You are a helpful AI assistant...'. Think of these instructions as a constitution guiding the AI assistant's interactions with users across different tasks.

Format your response as follows:
Critique: <Critique using less than {max_tokens_critique} tokens>
Revision: <Revised instructions using less than {max_tokens_revision} tokens>"""
    ),
}