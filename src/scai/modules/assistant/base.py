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
from scai.modules.assistant.prompts import ASSISTANT_PROMPTS
from scai.modules.memory.buffer import CustomConversationBufferWindowMemory

from langchain.chains.llm import LLMChain

class AssistantModel():
    """Chain for applying the AI Assitant.

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
        assistant_prompt: AssistantPrompt,
        max_tokens: int = 100, # max tokens to generate
    ) -> str:
        """Run assistant."""
        assistant_prompt_template = SystemMessagePromptTemplate.from_template(assistant_prompt.content)
        # convert chat into dict
        chat_message_dict = [self._convert_message_to_dict(m) for m in buffer.load_memory_variables(var_type="chat")['history']]
        # crate chat history
        chat_history = "\n".join([f"{m['role']}: {m['content']}" for m in chat_message_dict])
        # convert system message into dict
        system_message_dict = [self._convert_message_to_dict(m) for m in buffer.load_memory_variables(var_type="system", use_assistant_k=True)['history']] # only care about assistants system messages
        # create system message
        system_history = "\n".join([f"{m['role']}: {m['content']}" for m in system_message_dict]) # only care about last system message
        # create prompt 
        assistant_chat_prompt = ChatPromptTemplate.from_messages([assistant_prompt_template])
        # template
        template = assistant_chat_prompt.format(system_message=system_history,
                                                chat_history=chat_history,
                                                max_tokens=max_tokens)

        return template
         # # run asssiastant
        # chain = LLMChain(llm=self.llm, prompt=assistant_chat_prompt)
        # response = chain.run(system_message=system_history, chat_history=chat_history, max_tokens=max_tokens, stop=["System:"])
        # return response