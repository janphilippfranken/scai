from abc import ABC
from typing import (
    Any, 
    Dict, 
    Optional, 
    Tuple,
)

from pydantic import Field

from langchain.memory.utils import get_prompt_input_key
from langchain.schema import BaseMemory

from scai.modules.memory.history import CustomBaseChatMessageHistory
from scai.modules.memory.in_memory import CustomChatMessageHistory


class CustomBaseChatMemory(BaseMemory, ABC):
    # TODO: polish this class
    """
    Custom version of langchain that allows to store the system message https://github.com/hwchase17/langchain/blob/master/langchain/memory/chat_memory.py.
    """
    full_memory: CustomBaseChatMessageHistory = Field(default_factory=CustomChatMessageHistory) # memory for all messages
    system_memory: CustomBaseChatMessageHistory = Field(default_factory=CustomChatMessageHistory) # memory for system messages of the ai assistant
    chat_memory: CustomBaseChatMessageHistory = Field(default_factory=CustomChatMessageHistory) # memory for all chat messages
    user_chat_memory: CustomBaseChatMessageHistory = Field(default_factory=CustomChatMessageHistory) # chat memory from perspective of user
    assistant_chat_memory: CustomBaseChatMessageHistory = Field(default_factory=CustomChatMessageHistory) # chat memory from perspective of assistant
    """Using system, user, and assistant instead of input output keys"""
    full_key: Optional[str] = None
    system_key: Optional[str] = None
    chat_key: Optional[str] = None
    user_key: Optional[str] = None
    assistant_key: Optional[str] = None
    return_messages: bool = True
 
    def save_context(
        self, 
        # system 
        system: Optional[Dict[str, Any]] = None, 
        system_rating: Optional[str] = None,
        system_prompt: Optional[str] = None,
        system_message_id: Optional[str] = None,
        # user
        user: Optional[Dict[str, Any]] = None,
        user_rating: Optional[str] = None,
        user_prompt: Optional[str] = None,
        user_message_id: Optional[str] = None,
        # assistant
        assistant: Optional[Dict[str, Any]] = None,
        assistant_rating: Optional[str] = None,
        assistant_prompt: Optional[str] = None,
        assistant_message_id: Optional[str] = None,
    ) -> None:
        """Save context from this conversation to buffer of type  List[BaseMessage] = [].

        Args:
            system: The system message to be saved.
            system_rating: The system rating to be saved.
            system_prompt: The system prompt to be saved.
            system_message_id: The system message id to be saved.
            user: The user message to be saved.
            user_rating: The user rating to be saved.
            user_prompt: The user prompt to be saved.
            user_message_id: The user message id to be saved.
            assistant: The assistant message to be saved.
            assistant_rating: The assistant rating to be saved.
            assistant_prompt: The assistant prompt to be saved.
            assistant_message_id: The assistant message id to be saved.
            
        Returns:
            None
        """

        # system
        if system is not None:
            if self.system_key is None:
                system_key = get_prompt_input_key(system, self.memory_variables)   
            else:
                system_key = self.system_key

            self.system_memory.add_system_message(message=system[system_key], 
                                                  system_rating=system_rating,
                                                  system_prompt=system_prompt,
                                                  system_message_id=system_message_id)
            
            self.full_memory.add_system_message(message=system[system_key], 
                                                system_rating=system_rating,
                                                system_prompt=system_prompt,
                                                system_message_id=system_message_id)
        # user
        if user is not None:
            if self.user_key is None:
                user_key = get_prompt_input_key(user, self.memory_variables)   
            else:
                user_key = self.user_key

            self.user_chat_memory.add_assistant_message(message=user[user_key], # for reversing roles
                                                        assistant_rating=user_rating, 
                                                        assistant_prompt=user_prompt,
                                                        assistant_message_id=user_message_id)
            
            self.assistant_chat_memory.add_user_message(message=user[user_key], 
                                                        user_rating=user_rating, 
                                                        user_prompt=user_prompt,
                                                        user_message_id=user_message_id)
            
            self.chat_memory.add_user_message(message=user[user_key], 
                                              user_rating=user_rating, 
                                              user_prompt=user_prompt,
                                              user_message_id=user_message_id)
            
            self.full_memory.add_user_message(message=user[user_key], 
                                              user_rating=user_rating, 
                                              user_prompt=user_prompt,
                                              user_message_id=user_message_id)
        # assistant
        if assistant is not None:
            if self.assistant_key is None:
                assistant_key = get_prompt_input_key(assistant, self.memory_variables)   
            else:
                assistant_key = self.assistant_key
            
            self.assistant_chat_memory.add_assistant_message(message=assistant[assistant_key], 
                                                             assistant_rating=assistant_rating, 
                                                             assistant_prompt=assistant_prompt,
                                                             assistant_message_id=assistant_message_id)     
              
            self.user_chat_memory.add_user_message(message=assistant[assistant_key],  # for reversing roles
                                                   user_rating=assistant_rating, 
                                                   user_prompt=assistant_prompt,
                                                   user_message_id=assistant_message_id)
            
            self.chat_memory.add_assistant_message(message=assistant[assistant_key], 
                                                   assistant_rating=assistant_rating, 
                                                   assistant_prompt=assistant_prompt,
                                                   assistant_message_id=assistant_message_id)
            
            self.full_memory.add_assistant_message(message=assistant[assistant_key], 
                                                   assistant_rating=assistant_rating,
                                                   assistant_prompt=assistant_prompt, 
                                                   assistant_message_id=assistant_message_id)

    def clear(self) -> None:
        """Clear memory contents."""
        self.chat_memory.clear()