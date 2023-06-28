from typing import (
    List, 
    Optional,
)

from abc import ABC, abstractmethod

from langchain.schema import (
    BaseMessage,
    SystemMessage,
    HumanMessage,
    AIMessage,
)

class CustomBaseChatMessageHistory(ABC):
    """Base interface for chat message history
    See `ChatMessageHistory` for default implementation.
    """

    """
    Example:
        .. code-block:: python

            class FileChatMessageHistory(BaseChatMessageHistory):
                storage_path:  str
                session_id: str

               @property
               def messages(self):
                   with open(os.path.join(storage_path, session_id), 'r:utf-8') as f:
                       messages = json.loads(f.read())
                    return messages_from_dict(messages)

               def add_message(self, message: BaseMessage) -> None:
                   messages = self.messages.append(_message_to_dict(message))
                   with open(os.path.join(storage_path, session_id), 'w') as f:
                       json.dump(f, messages)
               
               def clear(self):
                   with open(os.path.join(storage_path, session_id), 'w') as f:
                      s f.write("[]")
    """

    messages: List[BaseMessage]

    def add_system_message(self, message: str, system_rating: Optional[str]=None, system_prompt: Optional[str]=None, system_message_id: Optional[str]=None) -> None:
        """Add a system message to the store"""
        self.add_message(SystemMessage(content=message), rating=system_rating, prompt=system_prompt, message_id=system_message_id)
    
    def add_user_message(self, message: str, user_rating: Optional[str]=None, user_prompt: Optional[str]=None, user_message_id: Optional[str]=None) -> None:
        """Add a user message to the store"""
        self.add_message(HumanMessage(content=message), rating=user_rating, prompt=user_prompt, message_id=user_message_id)

    def add_assistant_message(self, message: str, assistant_rating: Optional[str]=None, assistant_prompt: Optional[str]=None, assistant_message_id: Optional[str]=None) -> None:
        """Add an AI message to the store"""
        self.add_message(AIMessage(content=message), rating=assistant_rating, prompt=assistant_prompt, message_id=assistant_message_id)
     
    def add_message(self, message: BaseMessage, rating: Optional[str]=None, prompt: Optional[str]=None, message_id: Optional[str]=None) -> None:
        """Add a self-created message to the store"""
        raise NotImplementedError

    @abstractmethod
    def clear(self) -> None:
        """Remove all messages from the store"""