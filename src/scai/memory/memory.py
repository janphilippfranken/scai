from typing import (
    Any, 
    Dict, 
    List, 
)

class ChatMemory():
    """
    Chat memory
    """
    def __init__(self) -> None:
        self.messages: Dict[str, List[Any]] = {}

    def add_message(
        self, 
        message_id: str,
        **kwargs,
    ) -> None:
        """add messages to the store"""
        if self.messages.get(message_id) is None:
            self.messages[message_id] = []
        self.messages[message_id].append(kwargs)