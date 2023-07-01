from typing import (
    Any, 
    Dict, 
    List, 
    Optional,
)

from scai.memory.chat import ChatMemory 

from langchain.schema import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ChatMessage,
)


class ConversationBuffer(ChatMemory):
    """
    Custom conversation buffer.
    """
    def __init__(self, system_k: int=5, chat_k: int=5) -> None:
        self.system_k: int = 5 
        self.chat_k: int = 5 
        self.meta_memory: ChatMemory = ChatMemory()
        self.chat_memory: ChatMemory = ChatMemory()
        self.full_memory: ChatMemory = ChatMemory()

    @property
    def full_buffer(self) -> Dict[str, List[Any]]:
        return self.full_memory.message_dict
    
    @property
    def meta_buffer(self) -> Dict[str, List[Any]]:
        return self.meta_memory.message_dict
    
    @property
    def chat_buffer(self) -> Dict[str, List[Any]]:
        return self.chat_memory.message_dict
    
    def save_system_context(self, message, system_message_id, **kwargs) -> None:
        self.full_memory.add_message(message, message_id=system_message_id, **kwargs)
        self.meta_memory.add_message(message, message_id=system_message_id, **kwargs)
        
    def save_user_context(self, message, user_message_id, **kwargs) -> None:
        self.chat_memory.add_message(message, message_id=user_message_id, **kwargs)
        self.full_memory.add_message(message, message_id=user_message_id, **kwargs)
        
    def save_assistant_context(self, message, assistant_message_id, **kwargs) -> None:
        self.chat_memory.add_message(message, message_id=assistant_message_id, **kwargs)
        self.full_memory.add_message(message, message_id=assistant_message_id, **kwargs) 
    
    def load_memory_variables(self, 
                              var_type: str="system",
    ) -> Dict[str, str]:
        """Return history buffer for system.
        
        Args:
            
        Returns:
            Dictionary of memory variables.
        """
        if var_type == "system":
            return self.meta_buffer
        elif var_type == "chat":
            return self.chat_buffer
        elif var_type == "full":
            return self.full_buffer