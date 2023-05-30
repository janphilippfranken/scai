"""meta-prompt."""
from typing import (
    Any,
    Dict,
    List, 
    Optional
)



from scai.modules.memory.buffer import CustomConversationBufferWindowMemory

memory = CustomConversationBufferWindowMemory(k=1)
memory.save_context({"system": "you are a helpful ai assistant"}, {"user": "hi"}, {"assistant": "how are you"})



print(memory)