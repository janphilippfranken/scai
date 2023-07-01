from typing import (
    Any, 
    Dict, 
    List, 
    Optional,
)

from langchain.schema import (
    BaseMessage,
)

class ChatMemory():
    """
    Custom chat memory
    """
    def __init__(self) -> None:
        self.message_ids: List[str] = []
        self.message_dict: Dict[str, List[Any]] = {}

    def add_message(
        self, 
        message: BaseMessage, 
        message_id: str,
        **kwargs,
    ) -> None:
        """Add messages to the store"""
        self.message_ids.append(message_id)
        if self.message_dict.get(message_id) is None:
            self.message_dict[message_id] = []
        self.message_dict[message_id].append({'message': message, **kwargs})
