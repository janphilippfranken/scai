"""The Assistant."""
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

from scai.modules.assistant.models import AssistantPrompt
from scai.modules.assistant.assistant_prompt import ASSISTANT_PROMPTS
from scai.modules.memory.buffer import CustomConversationBufferWindowMemory

from langchain.chains.llm import LLMChain

class AssistantChain():
    """Chain for applying the AI Assitant.

    Example:
        .. code-block:: python

            

    """

    def __init__(self, llm) -> None:
        self.llm = llm

    @classmethod
    def get_prompts(
        cls, names: Optional[List[str]] = None
    ) -> List[AssistantPrompt]:
        return list(ASSISTANT_PROMPTS.values()) if names is None else [ASSISTANT_PROMPTS[name] for name in names]
    
    @classmethod 
    def get_template(
        cls, name: str
    ) -> str:
        """Get meta-prompt (i.e. meta system message) based on name."""
        return cls.get_prompts([name])[0].content
    
    def _convert_message_to_dict(message: BaseMessage) -> dict:
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
        name: str,
        buffer: Optional[CustomConversationBufferWindowMemory],
        revised_assistant_prompt: Optional[AssistantPrompt], # this is the optional revised assistant template
        turns: Optional[int] = 1, # how many turns to feed into the prompt
    ) -> str:
        """Run assistant."""
        # get the assistant system message
        assistant_system_message = SystemMessage(content=self.get_template(name=name).content)
        # if the revised assistant prompt is not none, update the assistant's system message
        if revised_assistant_prompt is not None:
            assistant_system_message.content = revised_assistant_prompt.content
        # get messages
        messages = [assistant_system_message] + buffer.chat_memory.messages[1:] # removing the old system message
        # convert to dict
        message_dict = [self._convert_message_to_dict(m) for m in messages]
        # run assistant 
        chain = LLMChain(llm=self.llm, prompt=message_dict)
        response = chain.run(stop=["System:"])
        
        return response
    
