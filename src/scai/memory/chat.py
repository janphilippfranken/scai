from typing import (
    Any, 
    Dict, 
    Optional, 
    Tuple,
)

from pydantic import Field

from langchain.memory.utils import get_prompt_input_key
from langchain.schema import BaseMemory

from scai.memory.history import CustomBaseChatMessageHistory
from scai.memory.in_memory import CustomChatMessageHistory


class CustomBaseChatMemory(BaseMemory):
    """Manages multiple conversation message histories."""
    chat_memory: CustomBaseChatMessageHistory = Field(default_factory=CustomChatMessageHistory) 
    user_chat_memory: CustomBaseChatMessageHistory = Field(default_factory=CustomChatMessageHistory)
    assistant_chat_memory: CustomBaseChatMessageHistory = Field(default_factory=CustomChatMessageHistory)
    
    def save_meta_context(self, meta_message_id, **kwargs) -> None:
        self.chat_memory.add_meta_message(message_id=meta_message_id, **kwargs)
        self.user_chat_memory.add_meta_message(message_id=meta_message_id, **kwargs)
        self.assistant_chat_memory.add_meta_message(message_id=meta_message_id, **kwargs)
        
    def save_user_context(self, user_message_id, **kwargs) -> None:
        self.chat_memory.add_user_message(message_id=user_message_id, **kwargs)
        self.assistant_chat_memory.add_user_message(message_id=user_message_id, **kwargs) 
        
    def save_assistant_context(self, assistant_message_id, **kwargs) -> None:
        self.chat_memory.add_assistant_message(message_id=assistant_message_id, **kwargs)
        self.user_chat_memory.add_assistant_message(message_id=assistant_message_id, **kwargs)  
        
    def save_context(self, **kwargs) -> None:
        if 'meta_message_id' in kwargs:
            self.save_system_context(**kwargs)
        elif 'user_message_id' in kwargs:
            self.save_user_context(**kwargs)
        elif 'assistant_message_id' in kwargs:
            self.save_assistant_context(**kwargs)
            
    def clear(self) -> None:
        self.chat_memory.clear()
        self.user_chat_memory.clear() 
        self.assistant_chat_memory.clear()