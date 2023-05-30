"""
Adapted from https://github.com/hwchase17/langchain/blob/master/langchain/memory/buffer_window.py
"""
from typing import Any, Dict, List, Optional

from scai.modules.memory.chat import CustomBaseChatMemory
from langchain.schema import BaseMessage, get_buffer_string


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
        print(buffer)
        if not self.return_messages:
            buffer = get_buffer_string(
                buffer,
                system_prefix=self.system_prefix,
                user_prefix=self.user_prefix,
                assistant_prefix=self.assistant_prefix,
            )
        return {self.memory_key: buffer}