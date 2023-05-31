"""
The Assistant Contract.
"""
from typing import Dict
    
from scai.modules.assistant.models import AssistantContract

ASSISTANT_CONTRACT: Dict[str, AssistantContract] = {
    "assistant_contract_1": AssistantContract(
        name="assistant_contract_1",
        role="system",
        content="You are a helpful assistant.",
    ),
}
