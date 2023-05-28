"""
The User Contract.
"""
from typing import Dict
    
from modules.user.models import UserContract

USER_CONTRACT: Dict[str, UserContract] = {
    "user_message_1": UserContract(
        name="user_message_1",
        role="user",
        content="You dont like long conversations.",
    ),
}
