"""The Assistant."""
from typing import (
    Any,
    Dict,
    List, 
    Optional
)

from langchain.chains.base import Chain
from langchain.chains.llm import LLMChain

from modules.assistant.models import AssistantContract
from modules.assistant.assistant_contract import ASSISTANT_CONTRACT


class AssistantChain(Chain):
    """Chain for applying the AI Assitant.

    Example:
        .. code-block:: python

            

    """

    chain: LLMChain
    assistant_contract: List[AssistantContract]
    assistant_chain: LLMChain

    # TODO: @sam: build this class, take inspiration from https://github.com/hwchase17/langchain/blob/master/langchain/chains/constitutional_ai/base.py

    raise NotImplementedError()