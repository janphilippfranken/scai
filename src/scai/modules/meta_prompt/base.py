"""meta-prompt."""
from typing import (
    Any,
    Dict,
    List, 
    Optional
)


from langchain.memory import ConversationBufferWindowMemory

memory = ConversationBufferWindowMemory(k=1)
memory.save_context({"system": "you are a helpful ai assistant"}, {"user": "hi"}, {"assistant": "how are you"})



print(memory)