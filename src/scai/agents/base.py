from typing import (
    Any,
    Dict,
    List, 
    Optional,
    Tuple,
)

from abc import ABC, abstractmethod

from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

from langchain.chains.llm import LLMChain
from langchain.chat_models.base import BaseChatModel

import numpy as np # for simulated responses

from scai.prompts.user.models import UserPrompt
from scai.prompts.task.models import TaskPrompt
from scai.prompts.metrics.models import MetricPrompt

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
        """Initializes a chat model of type user, assistant, or meta-prompt.

        Args:
            llm: The LLM Chat model. Currently either a CRFM or OpenAI model chat model
            model_id: The unique identifier of the model
        """
        self.llm = llm
        self.model_id = model_id

    @abstractmethod
    def _get_n_user(
        self, 
        chat_memory: ChatMemory,
    ) -> int:
        """
        Returns the number of users in the chat memory.
        
        Args:
            sorted_model_ids: The sorted list of message ids.
            
        Returns:    
            The number of users in the conversation."""
        return len(set(id.split('_')[0] for id in chat_memory.keys()))
    
    def _get_model_ids(
        self, 
        chat_memory: ChatMemory,
        model_type: str,
    ) -> List[str]:
        """
        Returns the model ids of type model_type from the chat memory.
        
        Args:
            chat_memory: The chat memory.
            model_type: The type of model to return.
            
        Returns:    
            List of model ids of type model_type.
        """
        return [key for key in list(chat_memory.keys()) if model_type in key]
    
    @abstractmethod
    def _get_chat_history(
        self,
        buffer: ConversationBuffer,
        memory_type: str,
    ) -> List[str]:
        """
        Get chat history

        Args:
            buffer: Conversation buffer
            memory_type: Type of memory to load

        Returns:
            List of chat history strings
        """
        if memory_type == "system":
            return buffer.load_memory_variables(memory_type='system')[self.model_id]
        elif memory_type == "chat":
            return buffer.load_memory_variables(memory_type='chat')[self.model_id]
        
    def _get_collective_chat_history(
        self,
        buffer: ConversationBuffer,
    ) -> Dict[str, Any]:
        """
        Get most recent responses from other user conversations

        Args:
            buffer: Conversation buffer

        Returns:
            List of chat history strings
        """
        collective_chat_history = {}
        for key in buffer.load_memory_variables(memory_type='chat').keys():
            if key != self.model_id and '_user' in key:
                collective_chat_history[key] = buffer.load_memory_variables(memory_type='chat')[key][-1] # get most recent response only
        return collective_chat_history
    
    @abstractmethod
    def _get_chat_history_prompt_templates(self):
        raise NotImplementedError

    @abstractmethod
    def _get_prompt(
        self, 
    ) -> Tuple[ChatPromptTemplate, str]:
        """
        Get the prompt fed into the model. 
        """
        raise NotImplementedError

    @abstractmethod
    def _get_response(
        self):
        """
        Get the response from the model. 
        """
        raise NotImplementedError

    @abstractmethod
    def _format_response(
        self,
        response: str, 
        variables: list,
    ) -> Dict[str, str]:
        """
        Format string response as dictionary of target variables and values.
        """
        var_dict = {}
        for lines in response.splitlines():
            for var in variables:
                if f'{var}:' in lines:
                    var_dict[var] = lines.split(': ')[1].strip()
        return var_dict

    @abstractmethod 
    def run(self):
        """
        Run the agent.
        """
        raise NotImplementedError