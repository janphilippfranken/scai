"""The Assistant."""
from typing import (
    Any,
    Dict,
    List, 
    Optional
)

from langchain.chains.base import Chain
from langchain.chains.llm import LLMChain

from scai.modules.assistant.models import AssistantPrompt
from scai.modules.assistant.assistant_prompt import ASSISTANT_PROMPT


class AssistantChain(Chain):
    """Chain for applying the AI Assitant.

    Example:
        .. code-block:: python

            

    """

    chain: LLMChain
    assistant_contract: List[AssistantPrompt]
    assistant_chain: LLMChain

    # TODO: @sam: build this class, take inspiration from https://github.com/hwchase17/langchain/blob/master/langchain/chains/constitutional_ai/base.py

    raise NotImplementedError()