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
    
    def _convert_message_to_dict(message: BaseMessage) -> dict:
        if isinstance(message, ChatMessage):
            message_dict = {"role": message.role, "content": message.content}
        elif isinstance(message, HumanMessage):
            message_dict = {"role": "user", "content": message.content}
        elif isinstance(message, AIMessage):
            message_dict = {"role": "user", "content": message.content}
        elif isinstance(message, SystemMessage):
            message_dict = {"role": "system", "content": message.content}
        else:
            raise ValueError(f"Got unknown type {message}")
        if "name" in message.additional_kwargs:
            message_dict["name"] = message.additional_kwargs["name"]
        return message_dict
    
    def sort_messages(self):
        pass

    def run(
        self,
        name: str,
        buffer: Optional[CustomConversationBufferWindowMemory],
        revised_user_prompt: Optional[UserPrompt], # this is the optional revised user template
        turns: Optional[int] = 1, # how many turns to feed into the prompt
    ) -> str:
        """Run user."""
        # get the user system message
        user_system_message = SystemMessage(content=self.get_template(name=name).content)
        # if the revised user prompt is not none, update the user's system message
        if revised_user_prompt is not None:
            user_system_message.content = revised_user_prompt.content
        # get messages
        messages = [user_system_message] + buffer.chat_memory.messages[1:] # removing the old system message
        # convert to dict
        message_dict = [self._convert_message_to_dict(m) for m in messages] # check if messages have to be sorted
        # run user 
        chain = LLMChain(llm=self.llm, prompt=message_dict)
        response = chain.run(stop=["System:"])
        
        return response
    
