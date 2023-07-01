from typing import (
    Any, 
    Dict, 
    List,
)

from scai.memory.memory import ChatMemory 

class ConversationBuffer(ChatMemory):
    """
    A class to manage conversation buffers.
    """
    def __init__(self) -> None:
        self._meta_memory: ChatMemory = ChatMemory()
        self._chat_memory: ChatMemory = ChatMemory()
        self._full_memory: ChatMemory = ChatMemory()

    @property
    def full_buffer(self) -> Dict[str, List[Any]]:
        return self._full_memory.messages
    
    @property
    def meta_buffer(self) -> Dict[str, List[Any]]:
        return self._meta_memory.messages
    
    @property
    def chat_buffer(self) -> Dict[str, List[Any]]:
        return self._chat_memory.messages
    
    def save_system_context(self, message_id, **kwargs) -> None:
        """Stores system context."""
        self._full_memory.add_message(message_id=message_id, **kwargs)
        self._meta_memory.add_message(message_id=message_id, **kwargs)
        
    def save_user_context(self, message_id, **kwargs) -> None:
        """Stores user context."""
        self._chat_memory.add_message(message_id=message_id, **kwargs)
        self._full_memory.add_message(message_id=message_id, **kwargs)
        
    def save_assistant_context(self, message_id, **kwargs) -> None:
        """Stores assistant context."""
        self._chat_memory.add_message(message_id=message_id, **kwargs)
        self._full_memory.add_message(message_id=message_id, **kwargs)
    
    def load_memory_variables(self, var_type: str="system") -> Dict[str, str]:
        """
        Returns history buffer for given variable type.
        
        Args:
            var_type: A string indicating the type of memory to load. Should be one of 
                      "system", "chat", "full". 

        Returns:
            Dictionary of memory variables. If invalid `var_type` is provided, it returns 
            an error message.
        """
        if var_type == "system":
            return self.meta_buffer
        elif var_type == "chat":
            return self.chat_buffer
        elif var_type == "full":
            return self.full_buffer
        else:
            raise ValueError(f'Invalid var_type "{var_type}". Expected one of: "system", "chat", "full".')
