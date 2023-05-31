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
    return_messages: bool = True
 
    def save_context(
            self, 
            system: Optional[Dict[str, Any]] = None, 
            user: Optional[Dict[str, Any]] = None,
            assistant: Optional[Dict[str, Any]] = None,
        ) -> None:
        """Save context from this conversation to buffer of type  List[BaseMessage] = []."""
        """Get content of the system, user, and assistant messages."""
        if system is not None:
            if self.system_key is None:
                system_key = get_prompt_input_key(system, self.memory_variables)   
            else:
                system_key = self.system_key
            self.chat_memory.add_system_message(system[system_key])
        if user is not None:
            if self.user_key is None:
                user_key = get_prompt_input_key(user, self.memory_variables)   
            else:
                user_key = self.user_key
            self.chat_memory.add_user_message(user[user_key])
        if assistant is not None:
            if self.assistant_key is None:
                assistant_key = get_prompt_input_key(assistant, self.memory_variables)   
            else:
                assistant_key = self.assistant_key
            self.chat_memory.add_assistant_message(assistant[assistant_key])            

    def clear(self) -> None:
        """Clear memory contents."""
        self.chat_memory.clear()