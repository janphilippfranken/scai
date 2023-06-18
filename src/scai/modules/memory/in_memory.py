"""
Custom version of langchain that allows to store the system message https://github.com/hwchase17/langchain/blob/master/langchain/memory/chat_message_histories/in_memory.py
"""
from typing import List, Optional, Dict, Any

from pydantic import BaseModel

from langchain.schema import (
    BaseMessage,
)

from scai.modules.memory.history import CustomBaseChatMessageHistory


class CustomChatMessageHistory(CustomBaseChatMessageHistory, BaseModel):
    messages: List[BaseMessage] = []
    message_ids: List[str] = []
    ratings: List[str] = []
    message_dict: Dict[str, List[Any]] = {}

    def add_message(self, message: BaseMessage, rating: Optional[str]=None, message_id: Optional[str]=None) -> None:
        """Add a self-created message to the store"""
        if message_id is not None:
            self.message_ids.append(message_id)
            if self.message_dict.get(message_id) is None:
                self.message_dict[message_id] = []
            self.message_dict[message_id].append({'message': message, 'rating': rating})
        self.messages.append(message)

    def clear(self) -> None:
        self.messages = []