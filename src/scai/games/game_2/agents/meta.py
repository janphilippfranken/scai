from typing import Dict, Any

import numpy as np
import copy
import os

from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

from langchain import LLMChain
from langchain.chat_models.base import BaseChatModel

from scai.memory.memory import ChatMemory

from scai.games.game_2.prompts.meta.models import MetaPrompt
from scai.memory.buffer import ConversationBuffer
from scai.games.game_2.prompts.task.models import TaskPrompt

from scai.games.game_2.agents.base import BaseAgent

class MetaPromptModel(BaseAgent):
    """
    LLM Chain for running the meta-prompt agent.
    """
    def __init__(
        self, 
        llm: BaseChatModel, 
        model_id: str, 
    ) -> None:
        super().__init__(llm, model_id)
        
    def _get_chat_str(
        self,
        chat_history: ChatMemory,
        task_prompt: TaskPrompt,
    ) -> str:
        """
        Formats the chat history into a string which is placed within the meta-prompt prompt.

        Args:
            chat_history: (ChatMemory) The chat history.
            metric_prompt: (MetricPrompt) The metric prompt.
            task_prompt: (TaskPrompt) The task prompt.
            max_tokens_assistant: (int) The maximum number of tokens for the assistant.

        Returns:
            The chat history string.
        """
        # data structures for storing chat
        chat_history_string = ""
        for i, interactions in enumerate(chat_history.items()):
            # get the agent and the response
            agent, interaction = interactions
            # if we're on a dictator iteration, append the task
            if not i & 1:
                chat_history_string += f"{task_prompt.preamble}\n"
            # append the response
            chat_history_string += f"{agent.split('_')[1]}'s Response: {interaction[0]['response']}\n"
            # if we're on a decider iteration, signify the end of the interaction
            if i & 1:
                chat_history_string += f"End of interaction {str(i // 2)}\n"
        return chat_history_string
    
    def _get_prompt(
        self,
        meta_prompt: MetaPrompt,
    ) -> ChatPromptTemplate:
        """
        Returns the prompt template for meta-prompt.

        Args:
            meta_prompt: (MetaPrompt) The meta-prompt.

        Returns:
            The prompt template.
        """
        meta_prompt_template = HumanMessagePromptTemplate.from_template(meta_prompt.content)
        system_prompt_template = SystemMessagePromptTemplate.from_template("Always respond to the best of your ability.\n")
        return ChatPromptTemplate.from_messages([system_prompt_template, meta_prompt_template])
    
    def _get_response(
        self,
        chat_prompt_template: ChatPromptTemplate,
        social_contract: str,
        chat_history_string: str,
        #meta_prompt: MetaPrompt,
    ) -> str:
        """
        Returns the response from meta-prompt.

        Args:   
            chat_prompt_template: (ChatPromptTemplate) The chat prompt template.
            developer_constitution: (str) The developer constitution.
            social_contract: (str) The social contract.
            chat_history: (ChatMemory) The chat history.

        Returns:
            The response from meta-prompt.
        """
        chain = LLMChain(llm=self.llm, prompt=chat_prompt_template)
        response = chain.run(social_contract=social_contract,
                             chat_history=chat_history_string,
                             stop=['System:'])  
        return response

    def run(
        self,
        buffer: ConversationBuffer,
        meta_prompt: MetaPrompt,
        task_prompt: TaskPrompt,
        run: int,
        verbose: bool = False,
    ) -> str:
        """Runs meta-prompt

        Args:
            buffer (ConversationBuffer): The conversation buffer
            meta_prompt (MetaPrompt): The meta-prompt
            task_prompt (TaskPrompt): The task prompt
            metric_prompt (MetricPrompt): The metric prompt
            run (int): The run number
            test_run (bool, optional): Whether this is a test run. Defaults to False.
            verbose (bool, optional): Whether to print the meta-prompt. Defaults to False.
            max_tokens_meta (int, optional): The maximum number of tokens for the meta-prompt. Defaults to 100.
            max_tokens_assistant (int, optional): The maximum number of tokens for the assistant. Defaults to 100.

        Returns:
            A dictionary containing the input prompt and meta-prompt responses (revised system message, etc)
        """
        # get previous system messages (i.e. developer constitution and social contract)
        social_contract_string = self._get_chat_history(buffer, memory_type='system')['system'][-1]['response']
        # get chat history
        chat_history = self._get_chat_history(buffer, memory_type="chat")
        chat_history_string = self._get_chat_str(chat_history, task_prompt)
        # get meta-prompt template and string
        chat_prompt_template = self._get_prompt(meta_prompt)
        prompt_string = chat_prompt_template.format(social_contract=social_contract_string,
                                                    chat_history=chat_history_string)
        response = self._get_response(chat_prompt_template, 
                                      social_contract_string,
                                      chat_history_string)
        
        if verbose:
            print('===================================')
            print(f'META {str(self.model_id)}')
            print('prompt')
            print(prompt_string)
            print(response)
        
        return {
                'prompt': prompt_string,
                'response': response,
                'full_response': response,
                'run': run,
            }
