"""
The System Contract. This is equivalent to the `system message' information chat bots.
"""
from typing import Dict
    
from scai.systen.models import SystemContract

CONTRACT: Dict[str, SystemContract] = {
    "system_message_1": SystemContract(
        name="system_message_1",
        role="system",
        content="You are a helpful assistant.",
    ),
}