from typing import (
    Any, 
    Dict, 
    List, 
)

class ChatMemory():
    """
    Chat memory for storing conversation histories.
    """
    def __init__(self) -> None:
        self.messages: Dict[str, List[Any]] = {}

    def add_message(
        self, 
        model_id: str,
        **kwargs,
    ) -> None:
        """add messages to the store for each model_id"""
        if self.messages.get(model_id) is None:
            self.messages[model_id] = []
        self.messages[model_id].append(kwargs)