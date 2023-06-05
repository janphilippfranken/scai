"""meta-prompt."""
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

from scai.modules.meta_prompt.models import MetaPrompt
from scai.modules.meta_prompt.prompts import META_PROMPTS
from scai.modules.memory.buffer import CustomConversationBufferWindowMemory

from langchain import LLMChain

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


class MetaPromptModel():
    """Code for running meta-prompt.
    Example:
        .. code-block:: python
    """

    def __init__(self, llm) -> None:
        self.llm = llm

    @classmethod
    def get_prompts(
        cls, names: Optional[List[str]] = None
    ) -> List[MetaPrompt]:
        return list(META_PROMPTS.values()) if names is None else [META_PROMPTS[name] for name in names]
    
    @classmethod 
    def get_template(
        cls, name: str
    ) -> str:
        """Get meta-prompt (i.e. meta system message) based on name."""
        return cls.get_prompts([name])[0].content

    def run(
        self,
        name: str,
        buffer: CustomConversationBufferWindowMemory,
        turns: int = 1,
    ) -> str:
        """Run meta-prompt."""
        # get a meta system template (i.e. message for meta prompt agent)
        meta_system_template = self.get_template(name=name)
        meta_system_message_prompt = SystemMessagePromptTemplate.from_template(meta_system_template)
        # convert conversation into dict
        message_dict = [_convert_message_to_dict(m) for m in buffer.chat_memory.messages]
        # crate chat history from dict TODO: remove system? 
        chat_history = "\n".join([f"{m['role']}: {m['content']}" for m in message_dict])
        # TODO: need to remove the meta human templates to another file
        meta_human_template_0 = """Please return a revised system message for the AI assistant to improve the quality of the conversation.
        Write it next to response below.
        Response:"""
        meta_human_message_prompt_0 = HumanMessagePromptTemplate.from_template(meta_human_template_0)
        # create prompt 
        meta_chat_prompt = ChatPromptTemplate.from_messages([meta_system_message_prompt, meta_human_message_prompt_0])
        # run meta-prompt
        chain = LLMChain(llm=self.llm, prompt=meta_chat_prompt)
        response = chain.run(chat_history=chat_history, stop=["System:"])
        
        return response
