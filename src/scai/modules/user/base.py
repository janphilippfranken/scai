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

    def __init__(self, llm) -> None:
        self.llm = llm

    @classmethod
    def get_prompts(
        cls, names: Optional[List[str]] = None
    ) -> List[UserPrompt]:
        return list(USER_PROMPTS.values()) if names is None else [USER_PROMPTS[name] for name in names]
    
    @classmethod 
    def get_template(
        cls, name: str
    ) -> str:
        """Get prompt (i.e. meta system message) based on name."""
        return cls.get_prompts([name])[0].content
    
    def run(
        self,
        buffer: CustomConversationBufferWindowMemory,
        user_prompt: UserPrompt,
        task_prompt: TaskPrompt,
    ) -> str:
        """Run user."""
        # user system message
        user_system_prompt = SystemMessagePromptTemplate.from_template(user_prompt.content) 
        # get chat history
        chat_history_prompts = [m for m in buffer.load_memory_variables(var_type="user")['history']]      
        # prompt to generate next completion based on history
        generate_next = """Provide a response including feedback using no more than {max_tokens} tokens."""
        generate_next_prompt = HumanMessagePromptTemplate.from_template(generate_next)
        # build prompt template
        user_chat_prompt = ChatPromptTemplate.from_messages([user_system_prompt, *chat_history_prompts, generate_next_prompt])
        response = user_chat_prompt.format(persona=user_prompt.persona,
                                           task=task_prompt.content,
                                           max_tokens=user_prompt.max_tokens)
        # run user
        # chain = LLMChain(llm=self.llm, prompt=user_chat_prompt)
        # response = chain.run(persona=user_prompt.persona,
        #                      task=task_prompt.content,
        #                      chat_history=chat_history,
        #                      max_tokens=max_tokens,
        #                      stop=["System:"])
        return response