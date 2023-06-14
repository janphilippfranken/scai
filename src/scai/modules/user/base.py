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
    
    def _convert_message_to_dict(self, message: BaseMessage) -> dict:
        if isinstance(message, ChatMessage):
            message_dict = {"role": message.role, "content": message.content}
        elif isinstance(message, HumanMessage):
            message_dict = {"role": "user", "content": message.content}
        elif isinstance(message, AIMessage):
            message_dict = {"role": "assistant", "content": message.content}
        elif isinstance(message, SystemMessage):
            message_dict = {"role": "system", "content": message.content}
        else:
            raise ValueError(f"Got unknown type {message}")
        if "name" in message.additional_kwargs:
            message_dict["name"] = message.additional_kwargs["name"]
        return message_dict
    
    def run(
        self,
        buffer: CustomConversationBufferWindowMemory,
        user_prompt: UserPrompt,
        task_prompt: TaskPrompt,
        max_tokens: int = 100, # max tokens to generate
    ) -> str:
        """Run meta-prompt."""
        user_prompt_template = SystemMessagePromptTemplate.from_template(user_prompt.content)
        # convert chat into dict
        chat_message_dict = [self._convert_message_to_dict(m) for m in buffer.load_memory_variables(var_type="chat")['history']]
        # crate chat history
        chat_history = "\n".join([f"{m['role']}: {m['content']}" for m in chat_message_dict])
        # create prompt 
        user_chat_prompt = ChatPromptTemplate.from_messages([user_prompt_template])
        template = user_chat_prompt.format(persona=user_prompt.persona,
                                           task=task_prompt.content,
                                           chat_history=chat_history,  
                                           max_tokens=max_tokens)
        return template
        # # run meta-prompt
        # chain = LLMChain(llm=self.llm, prompt=meta_chat_prompt)
        # response = chain.run(persona=user_prompt.persona,
        #                      task=task_prompt.content,
        #                      chat_history=chat_history,
        #                      max_tokens=max_tokens,
        #                      stop=["System:"])
        # return response
    
