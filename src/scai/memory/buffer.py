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
        
    @property
    def full_buffer(self) -> List[BaseMessage]:
        return self.full_memory.messages
    
    @property
    def system_buffer(self) -> List[BaseMessage]:
        return self.meta_memory.messages
    
    @property
    def chat_buffer(self) -> List[BaseMessage]:
        return self.chat_memory.messages
    
    
    def load_memory_variables(self, 
                              var_type: str="system",
    ) -> Dict[str, str]:
        """Return history buffer for system.
        
        Args:
            
        Returns:
            Dictionary of memory variables.
        """
        if var_type == "system":
            return self.system_buffer
        elif var_type == "chat":
            return self.chat_buffer
        elif var_type == "full":
            return self.full_buffer