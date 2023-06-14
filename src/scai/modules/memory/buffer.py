"""
Adapted from https://github.com/hwchase17/langchain/blob/master/langchain/memory/buffer_window.py
"""
from typing import Any, Dict, List, Optional

from scai.modules.memory.chat import CustomBaseChatMemory
from langchain.schema import BaseMessage


from langchain.schema import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ChatMessage,
)


def custom_get_buffer_string(
    messages: List[BaseMessage], system_prefix: str = "System", human_prefix: str = "Human", ai_prefix: str = "AI"
) -> str:
    """Get buffer string of messages."""
    string_messages = []
    for m in messages:
        if isinstance(m, HumanMessage):
            role = human_prefix
        elif isinstance(m, AIMessage):
            role = ai_prefix
        elif isinstance(m, SystemMessage):
            role = system_prefix
        elif isinstance(m, ChatMessage):
            role = m.role
        else:
            raise ValueError(f"Got unsupported message type: {m}")
        string_messages.append(f"{role}: {m.content}")
    return "\n".join(string_messages)

class CustomConversationBufferWindowMemory(CustomBaseChatMemory):
    """Buffer for storing conversation memory."""
    system_prefix: str = "System"
    user_prefix: str = "Human"
    assistant_prefix: str = "AI"
    memory_key: str = "history"  #: :meta private:
    system_k: int = 5 # how much we will go back in the system history
    chat_k: int = 5 # how much we will go back in the chat history (bot user and assistant)
    user_k: int = 5 # how much we will go back in the user chat history
    assistant_k: int = 5 # how much we will go back in the assistant chat history

    @property
    def full_buffer(self) -> List[BaseMessage]:
        """String buffer of memory."""
        return self.full_memory.messages
    
    @property
    def system_buffer(self) -> List[BaseMessage]:
        """String buffer of memory."""
        return self.system_memory.messages
    
    @property
    def chat_buffer(self) -> List[BaseMessage]:
        """String buffer of memory."""
        return self.chat_memory.messages
    
    @property
    def user_buffer(self) -> List[BaseMessage]:
        """String buffer of memory."""
        return self.user_memory.messages
    
    @property
    def assistant_buffer(self) -> List[BaseMessage]:
        """String buffer of memory."""
        return self.assistant_memory.messages

    @property
    def memory_variables(self) -> List[str]:
        """Will always return list of memory variables.

        :meta private:
        """
        return [self.memory_key]
    
    def load_memory_variables(self, var_type: str="system", use_assistant_k: bool=False) -> Dict[str, str]:
        """Return history buffer for system."""
        if var_type == "system":
            if use_assistant_k is True:
                buffer: Any = self.system_buffer[-self.assistant_k :] if self.assistant_k > 0 else []
            else:
                buffer: Any = self.system_buffer[-self.system_k :] if self.system_k > 0 else [] 
        elif var_type == "chat":
            buffer: Any = self.chat_buffer[-self.chat_k * 2 :] if self.chat_k > 0 else []
        elif var_type == "user":
            buffer: Any = self.user_buffer[-self.user_k :] if self.user_k > 0 else []
        elif var_type == "assistant":
            buffer: Any = self.assistant_buffer[-self.assistant_k :] if self.assistant_k > 0 else []
        elif var_type == "full":
            buffer: Any = self.full_buffer
       
        if not self.return_messages:
            buffer = custom_get_buffer_string(
                buffer,
                system_prefix=self.system_prefix,
                human_prefix=self.user_prefix,
                ai_prefix=self.assistant_prefix,
            )
        return {self.memory_key: buffer}