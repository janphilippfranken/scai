"""
The Assistant Contract.
"""
from typing import Dict
    
from scai.modules.assistant.models import AssistantContract

ASSISTANT_CONTRACT: Dict[str, AssistantContract] = {
    "assistant_message_1": AssistantContract(
        name="assistant_message_1",
        role="assistant",
        content="You are a helpful assistant.",
    ),
}



