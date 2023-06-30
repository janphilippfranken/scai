from typing import (
    Any, 
    Dict, 
    List, 
    Optional,
)

from scai.modules.memory.chat import CustomBaseChatMemory 

from langchain.schema import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ChatMessage,
)


def custom_get_buffer_string(
    messages: List[BaseMessage], 
    system_prefix: str = "System",
    human_prefix: str = "Human", 
    ai_prefix: str = "AI"
) -> str:
    """Get buffer string of messages.

    Args:
        messages: List of messages (following structure of https://platform.openai.com/docs/guides/gpt/chat-completions-api.).
        system_prefix: Prefix for system messages.
        human_prefix: Prefix for human messages.
        ai_prefix: Prefix for AI messages.

    Returns:
        String of messages.
    """
    string_messages = []
    for m in messages:
        if isinstance(m, HumanMessage):
            role = human_prefix
        elif isinstance(m, AIMessage):
            role = ai_prefix
        elif isinstance(m, SystemMessage):
            role = system_prefix
        elif isinstance(m, ChatMessage):
            role = m.role
        else:
            raise ValueError(f"Got unsupported message type: {m}")
        string_messages.append(f"{role}: {m.content}")
    return "\n".join(string_messages)

class CustomConversationBufferWindowMemory(CustomBaseChatMemory):
    """Custom buffer for storing conversation memory.
    Adapted from https://github.com/hwchase17/langchain/blob/master/langchain/memory/buffer_window.py.
    """
    system_prefix: str = "System"
    user_prefix: str = "Human"
    assistant_prefix: str = "AI"
    memory_key: str = "history"  # key for memory variables
    system_k: int = 5 # how much we will go back in the system history (i.e. meta-prompt memory)
    chat_k: int = 5 # how much we will go back in the chat history (ie joint user and assistant memory)
    user_k: int = 5 # how much we will go back in the user chat history (i.e. user memory)
    assistant_k: int = 5 # how much we will go back in the assistant chat history (i.e. assistant memory)
    assistant_system_k: int = 5 # how much we will go back in the assistant system history (i.e. assistant's system message memory)

    @property
    def full_buffer(self) -> List[BaseMessage]:
        return self.full_memory.messages
    
    @property
    def system_buffer(self) -> List[BaseMessage]:
        return self.system_memory.messages
    
    @property
    def chat_buffer(self) -> List[BaseMessage]:
        return self.chat_memory.messages
    
    @property
    def user_buffer(self) -> List[BaseMessage]:
        return self.user_chat_memory.messages
    
    @property
    def assistant_buffer(self) -> List[BaseMessage]:
        return self.assistant_chat_memory.messages

    @property
    def memory_variables(self) -> List[str]:
        return [self.memory_key]
    
    def load_memory_variables(self, 
                              var_type: str="system", 
                              use_assistant_system_k: bool=False,
    ) -> Dict[str, str]:
        """Return history buffer for system.
        
        Args:
            var_type: Type of memory variable to return.
            use_assistant_system_k: Whether to use assistant system k or not.
            
        Returns:
            Dictionary of memory variables.
        """
        if var_type == "system":
            if use_assistant_system_k is True:
                buffer: Any = self.system_buffer
            else:
                buffer: Any = self.system_buffer
        elif var_type == "chat":
            buffer: Any = self.chat_buffer
        elif var_type == "user":
            buffer: Any = self.user_buffer
        elif var_type == "assistant":
            buffer: Any = self.assistant_buffer
        elif var_type == "full":
            buffer: Any = self.full_buffer
       
        if not self.return_messages:
            buffer = custom_get_buffer_string(
                buffer,
                system_prefix=self.system_prefix,
                human_prefix=self.user_prefix,
                ai_prefix=self.assistant_prefix,
            )
        return {self.memory_key: buffer}