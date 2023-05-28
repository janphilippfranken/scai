"""The user/Developer Contract."""
from typing import (
    Any,
    Dict,
    List, 
    Optional
)

from langchain.chains.base import Chain
from langchain.chains.llm import LLMChain

from modules.user.models import UserContract
from modules.user.user_contract import USER_CONTRACT


class UserChain(Chain):
    """Chain for applying the user

    Example:
        .. code-block:: python

            

    """

    chain: LLMChain
    user_contract: List[UserContract]
    user_chain: LLMChain

    # TODO: @sam: build this class, take inspiration from https://github.com/hwchase17/langchain/blob/master/langchain/chains/constitutional_ai/base.py

    raise NotImplementedError()