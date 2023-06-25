"""The User."""
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

from scai.modules.user.models import UserPrompt
from scai.modules.user.prompts import USER_PROMPTS
from scai.modules.memory.buffer import CustomConversationBufferWindowMemory

from scai.modules.utils import get_vars_from_out

from scai.modules.task.models import TaskPrompt

from langchain.chains.llm import LLMChain

class UserModel():
    """Chain for applying the User.

    Example:
        .. code-block:: python

            

    """

    def __init__(self, llm, conversation_id) -> None:
        self.llm = llm
        self.conversation_id = conversation_id
    
    def run(
        self,
        buffer: CustomConversationBufferWindowMemory,
        user_prompt: UserPrompt,
        task_prompt: TaskPrompt,
        max_turns: int=5,
        verbose: bool=False,
    ) -> str:
        """Run user."""
        # user system message
        user_system_prompt = SystemMessagePromptTemplate.from_template(user_prompt.content) 
        # get conversation history
        chat_history_prompts = [
            message
            for message, message_id in zip(
                buffer.load_memory_variables(var_type="user")["history"],
                buffer.chat_memory.message_ids
            )
            if self.conversation_id in message_id
        ]
        # prompt to generate next completion based on history
        generate_next = """Rate the helpfulness of my response from 0 to 100 (where 0 = 0 percent satisfied and 100 = 100 percent satisfied). Additionally, provide feedback for improvement using less than {max_tokens} tokens.
Return your helpfulness rating and feedback in the following format: 
Rating: <helpfulness> 
Feedback: <feedback>."""
        generate_next_prompt = HumanMessagePromptTemplate.from_template(generate_next)
        # build prompt template
        user_chat_prompt = ChatPromptTemplate.from_messages([user_system_prompt, *chat_history_prompts, generate_next_prompt])
        # full prompt fed into the model
        prompt = user_chat_prompt.format(persona=user_prompt.persona,
                                            task=task_prompt.content,
                                            max_tokens=user_prompt.max_tokens,
                                            max_turns=max_turns - len(chat_history_prompts) // 2)
        # if verbose we just print the prompt and return it
        if verbose:
            print()
            print(f'USER {str(self.conversation_id)}')
            print(prompt)
            print()
            return {'Prompt': prompt, 'Rating': 50, 'Feedback': 'User_feedback_' + str(self.conversation_id)}
        
        # build chain
        chain = LLMChain(llm=self.llm, prompt=user_chat_prompt)
        # run chain
        response = chain.run(persona=user_prompt.persona,
                             task=task_prompt.content,
                             max_tokens=user_prompt.max_tokens,
                             max_turns=max_turns - len(chat_history_prompts) // 2,
                             stop=['System:'])
        # get vars from response
        response = get_vars_from_out(response, ['Rating', 'Feedback'])

        return {'Prompt': prompt, 'Rating': response['Rating'], 'Feedback': response['Feedback']}