"""
The User Contract.
"""
from typing import Dict
    
from scai.modules.user.models import UserContract

USER_CONTRACT: Dict[str, UserContract] = {
    "user_contract_1": UserContract(
        name="user_contract_1",
        role="system",
        content="You dont like long conversations.",
    ),
}