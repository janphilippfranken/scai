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
    k: int = 5

    @property
    def buffer(self) -> List[BaseMessage]:
        """String buffer of memory."""
        return self.chat_memory.messages

    @property
    def memory_variables(self) -> List[str]:
        """Will always return list of memory variables.

        :meta private:
        """
        return [self.memory_key]

    def load_memory_variables(self) -> Dict[str, str]:
        """Return history buffer."""
        buffer: Any = self.buffer[-self.k * 2 :] if self.k > 0 else []
        if not self.return_messages:
            buffer = custom_get_buffer_string(
                buffer,
                system_prefix=self.system_prefix,
                human_prefix=self.user_prefix,
                ai_prefix=self.assistant_prefix,
            )
        return {self.memory_key: buffer}