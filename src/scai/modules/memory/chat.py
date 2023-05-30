"""
Custom version of langchain that allows to store the system message https://github.com/hwchase17/langchain/blob/master/langchain/memory/chat_memory.py.
"""
from abc import ABC
from typing import Any, Dict, Optional, Tuple

from pydantic import Field

from langchain.memory.utils import get_prompt_input_key
from langchain.schema import BaseMemory

from scai.modules.memory.history import CustomBaseChatMessageHistory
from scai.modules.memory.in_memory import CustomChatMessageHistory


class CustomBaseChatMemory(BaseMemory, ABC):
    chat_memory: CustomBaseChatMessageHistory = Field(default_factory=CustomChatMessageHistory)
    """Using system, user, and assistant instead of input output keys"""
    system_key: Optional[str] = None
    user_key: Optional[str] = None
    assistant_key: Optional[str] = None
    return_messages: bool = False

    def _get_input_output(
        self, system: Dict[str, Any], user: Dict[str, Any], assistant: Dict[str, Any]
    ) -> Tuple[str, str]:
        """Get content of the system, user, and assistant messages."""
        if self.system_key is None:
            system_key = get_prompt_input_key(system, self.memory_variables)
        else:
            system_key = self.system_key
        if self.user_key is None:
            user_key = get_prompt_input_key(user, self.memory_variables)
        else:
            user_key = self.user_key
        if self.assistant_key is None:
            if len(assistant) != 1:
                raise ValueError(f"One assitant key expected, got {assistant.keys()}")
            assistant_key = list(assistant.keys())[0]
        else:
            assistant_key = self.assistant_key
        return system[system_key], user[user_key], assistant[assistant_key]

    def save_context(self, system: Dict[str, Any], user: Dict[str, Any], assistant: Dict[str, Any]) -> None:
        """Save context from this conversation to buffer of type  List[BaseMessage] = []."""
        system_str, user_str, assistant_str = self._get_input_output(system, user, assistant)
        self.chat_memory.add_system_message(system_str)
        self.chat_memory.add_user_message(user_str)
        self.chat_memory.add_assistant_message(assistant_str)

    def clear(self) -> None:
        """Clear memory contents."""
        self.chat_memory.clear()

