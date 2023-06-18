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
        generate_next = """Rate your satisfaction with my response, 1 being 'very dissatisfied' and 5 being 'very satisfied'. Additionally, provide feedback for improvement using less than {max_tokens} tokens.
Rating:
Feedback:"""
        generate_next_prompt = HumanMessagePromptTemplate.from_template(generate_next)
        # build prompt template
        user_chat_prompt = ChatPromptTemplate.from_messages([user_system_prompt, *chat_history_prompts, generate_next_prompt])
        response = user_chat_prompt.format(persona=user_prompt.persona,
                                           task=task_prompt.content,
                                           max_tokens=user_prompt.max_tokens,
                                           max_turns=max_turns - len(chat_history_prompts) // 2,
        )
        # run user
        # chain = LLMChain(llm=self.llm, prompt=user_chat_prompt)
        # response = chain.run(persona=user_prompt.persona,
        #                      task=task_prompt.content,
        #                      chat_history=chat_history,
        #                      max_tokens=max_tokens,
        #                      stop=["System:"])
        return "user" + str(self.conversation_id)