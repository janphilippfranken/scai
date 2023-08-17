from typing import (
    Any,
    Dict,
    List, 
)

from abc import ABC, abstractmethod

from langchain.prompts.chat import ChatPromptTemplate
from langchain.chat_models.base import BaseChatModel

from scai.memory.buffer import ConversationBuffer
from scai.memory.memory import ChatMemory

class BaseAgent(ABC):
    """
    Base agent class.
    """
    def __init__(
        self, 
        llm: BaseChatModel, 
        model_id: str, 
    ) -> None:
        """Initializes a chat model of type player or meta.

        Args:
            llm: The LLM Chat model. Currently either a CRFM or OpenAI model chat model
            model_id: The unique identifier of the model
        """
        self.llm = llm
        self.model_id = model_id

    @abstractmethod
    def _get_prompt(self) -> ChatPromptTemplate:
        """
        Get the prompt fed into the model. 
        """
        raise NotImplementedError

    @abstractmethod
    def _get_response(self) -> str:
        """
        Get the response from the model. 
        """
        raise NotImplementedError

    @abstractmethod 
    def run(self) -> Dict[str, Any]:
        """
        Run the agent.
        """
        raise NotImplementedError