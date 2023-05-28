"""
The System Contract.
"""
from typing import Dict
    
from scai.modules.system.models import SystemContract

SYSTEM_CONTRACT: Dict[str, SystemContract] = {
    "system_message_1": SystemContract(
        name="system_message_1",
        role="system",
        content="You are a helpful assistant.",
    ),
}