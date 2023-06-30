from typing import (
    Any,
    Dict,
    List, 
    Optional
)

from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

from langchain.schema import (
    AIMessage,
    BaseMessage,
    ChatMessage,
    HumanMessage,
    SystemMessage,
)

import numpy as np # for simulated responses

from langchain.chains.llm import LLMChain

from scai.modules.user.models import UserPrompt
from scai.modules.user.prompts import USER_PROMPTS
from scai.modules.memory.buffer import CustomConversationBufferWindowMemory
from scai.modules.task.models import TaskPrompt

from scai.modules.utils import get_vars_from_out


class UserModel():
    """LLM Chain for running the User."""

    def __init__(
        self, 
        llm, 
        conversation_id: str,
    ) -> None:
        """Initializes the UserModel with a given LLM and conversation id.

        Args:
            llm: The LLM Chat model.
            conversation_id: The unique identifier for the conversation the user had with assistant(s).
        """
        self.llm = llm
        self.conversation_id = conversation_id

    def _get_chat_history(
            self, 
            buffer: CustomConversationBufferWindowMemory,
        ) -> List[BaseMessage]:
        """Retrieves the chat history from the conversation buffer.

        Args:
            buffer: The buffer containing the conversation history.

        Returns:
            The conversation history.
        """
        return [
            message
            for message, message_id in zip(
                buffer.load_memory_variables(var_type="user")["history"],
                buffer.chat_memory.message_ids
            )
            if self.conversation_id in message_id
        ]

    
    def run(
        self,
        buffer: CustomConversationBufferWindowMemory,
        user_prompt: UserPrompt,
        task_prompt: TaskPrompt,
        test_run: bool = True,
        verbose: bool = False,
    ) -> Dict[str, Any]:
        """Runs the user.

        Args:
            buffer: The buffer containing the conversation history.
            user_prompt: The user prompt to be used.
            task_prompt: The task prompt to be used.
            test_run: Whether to run the user in test mode (i.e., without using tokens, just print prompt and save simulated response).
            verbose: Whether to print the prompt and response.

        Returns:
            A dictionary containing the input prompt and the user's rating and feedback.
        """
        user_system_prompt = SystemMessagePromptTemplate.from_template(user_prompt.content)
        chat_history_prompts = self._get_chat_history(buffer)
        generate_next = """Rate the satisfaction with my response on a 0-10 scale, where 0 means 'not at all satisfied' and 10 means 'completely satisfied'. To improve your future satisfaction, please provide feedback for how I can improve my responses in less {max_tokens} tokens.
Please format the response as follows:
Rating: <Your satisfaction rating>
Feedback: <Your improvement suggestions>"""
        generate_next_prompt = HumanMessagePromptTemplate.from_template(generate_next)
        user_chat_prompt = ChatPromptTemplate.from_messages([user_system_prompt, *chat_history_prompts, generate_next_prompt])

        # build prompt 
        prompt = user_chat_prompt.format(persona=user_prompt.persona,
                                         task=task_prompt.content,
                                         max_tokens=user_prompt.max_tokens)
        # if test_prompt, just print the prompt and return without using tokens
        if test_run:
            print()
            print(f'USER {str(self.conversation_id)}')
            print(prompt)
            print()
            return {'Prompt': prompt, 'Rating': np.random.randint(11), 'Feedback': 'User_feedback_' + str(self.conversation_id)}

        chain = LLMChain(llm=self.llm, prompt=user_chat_prompt)
        response = chain.run(persona=user_prompt.persona,
                             task=task_prompt.content,
                             max_tokens=user_prompt.max_tokens,
                             stop=['System:'])
        response = get_vars_from_out(response, ['Rating', 'Feedback'])
        if verbose:
            print()
            print("-----------------------------------")
            print("USER PROMPT")
            print(prompt)
            print("USER RESPONSE")
            print(response)
            print("-----------------------------------")
        return {'Prompt': prompt, 'Rating': response['Rating'], 'Feedback': response['Feedback']}