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


class MetaPromptModel():
    """Code for running meta-prompt.
    Example:
        .. code-block:: python
    """

    def __init__(self, llm) -> None:
        self.llm = llm
    
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
        meta_prompt: MetaPrompt,
    ) -> str:
        """Run meta-prompt."""
        meta_prompt_template = SystemMessagePromptTemplate.from_template(meta_prompt.content)
        # convert chat into dict
        chat_message_dict = [self._convert_message_to_dict(m) for m in buffer.load_memory_variables(var_type="chat")['history']]
        # crate chat history
        chat_history = "\n".join([f"{m['role']}: {m['content']}" for m in chat_message_dict])
        # convert system message into dict
        system_message_dict = [self._convert_message_to_dict(m) for m in buffer.load_memory_variables(var_type="system")['history']]
        # create system message
        system_history = "\n".join([f"{m['role']}: {m['content']}" for m in system_message_dict])
        # create prompt 
        meta_chat_prompt = ChatPromptTemplate.from_messages([meta_prompt_template])
        template = meta_chat_prompt.format(chat_history=chat_history,  
                                           system_history=system_history,
                                           max_tokens=meta_prompt.max_tokens)
        return template
        # # run meta-prompt
        # chain = LLMChain(llm=self.llm, prompt=meta_chat_prompt)
        # response = chain.run(chat_history=chat_history, assistant_system_message=system_history, max_tokens=max_tokens, stop=["System:"])
        # return response