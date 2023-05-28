"""The system."""
from typing import (
    Any,
    Dict,
    List, 
    Optional
)

from langchain.chains.base import Chain
from langchain.chains.llm import LLMChain

from modules.system.models import SystemContract
from modules.system.system_contract import SYSTEM_CONTRACT


class SystemChain(Chain):
    """Chain for applying the system.

    Example:
        .. code-block:: python

            

    """

    chain: LLMChain
    system_contract: List[SystemContract]
    system_chain: LLMChain

    # TODO: @sam: build this class, take inspiration from https://github.com/hwchase17/langchain/blob/master/langchain/chains/constitutional_ai/base.py

    raise NotImplementedError("SystemChain is not implemented yet.")