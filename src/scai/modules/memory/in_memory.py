"""
Custom version of langchain that allows to store the system message https://github.com/hwchase17/langchain/blob/master/langchain/memory/chat_message_histories/in_memory.py
"""
from typing import List

from pydantic import BaseModel

from langchain.schema import (
    BaseMessage,
)

from scai.modules.memory.history import CustomBaseChatMessageHistory


class CustomChatMessageHistory(CustomBaseChatMessageHistory, BaseModel):
    messages: List[BaseMessage] = []

    def add_message(self, message: BaseMessage) -> None:
        """Add a self-created message to the store"""
        self.messages.append(message)

    def clear(self) -> None:
        self.messages = []