from typing import (
    Any, 
    Dict, 
    List,
)

from scai.memory.memory import ChatMemory 

class ConversationBuffer(ChatMemory):
    """
    Managing different types of memory buffers (system, chat, memory).
    """
    def __init__(self) -> None:
        self._system_memory: ChatMemory = ChatMemory() # system memory: stores system messages generated by meta-prompt model
        self._chat_memory: ChatMemory = ChatMemory()   # chat memory: stores conversation history between user and assistant models
        self._full_memory: ChatMemory = ChatMemory()   # full memory: stores system and chat messages 

    @property
    def buffer(self) -> Dict[str, List[Any]]:
        return self._full_memory.messages
    
    @property
    def meta_buffer(self) -> Dict[str, List[Any]]:
        return self._system_memory.messages
    
    @property
    def chat_buffer(self) -> Dict[str, List[Any]]:
        return self._chat_memory.messages
    
    def save_system_context(self, model_id, **kwargs) -> None:
        """Stores system context."""
        self._full_memory.add_message(model_id=model_id, **kwargs)
        self._system_memory.add_message(model_id=model_id, **kwargs)
        
    def save_user_context(self, model_id, **kwargs) -> None:
        """Stores user context."""
        self._chat_memory.add_message(model_id=model_id, **kwargs)
        self._full_memory.add_message(model_id=model_id, **kwargs)
        
    def save_assistant_context(self, model_id, **kwargs) -> None:
        """Stores assistant context."""
        self._chat_memory.add_message(model_id=model_id, **kwargs)
        self._full_memory.add_message(model_id=model_id, **kwargs)
    
    def load_memory_variables(self, memory_type: str="system") -> Dict[str, str]:
        """
        Returns history buffer for given variable type.
        
        Args:
            memory_type: A string indicating the type of memory to load. Should be one of 
                      "system", "chat", "full". 

        Returns:
            Dictionary of memory variables. If invalid `memory_type` is provided, it returns 
            an error message.
        """
        if memory_type == "system":
            return self.meta_buffer
        elif memory_type == "chat":
            return self.chat_buffer
        elif memory_type == "full":
            return self.buffer
        else:
            raise ValueError(f'Invalid memory_type "{memory_type}". Expected one of: "system", "chat", "full".')