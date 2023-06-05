"""The user/Developer Prompt."""
from typing import (
    Any,
    Dict,
    List, 
    Optional
)

from langchain.chains.base import Chain
from langchain.chains.llm import LLMChain

from scai.modules.user.models import UserPrompt
from scai.modules.user.user_prompt import USER_PROMPT


class UserChain(Chain):
    """Chain for applying the user

    Example:
        .. code-block:: python

            

    """

    chain: LLMChain
    user_Prompt: List[UserPrompt]
    user_chain: LLMChain

    # TODO: @sam: build this class, take inspiration from https://github.com/hwchase17/langchain/blob/master/langchain/chains/constitutional_ai/base.py

    raise NotImplementedError()