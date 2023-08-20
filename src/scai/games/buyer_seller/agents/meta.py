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

from scai.games.red_teaming.prompts.meta.models import MetaPrompt
from scai.memory.buffer import ConversationBuffer
from scai.games.red_teaming.prompts.task.models import TaskPrompt
from scai.games.red_teaming.prompts.metrics.models import MetricPrompt

from scai.games.red_teaming.agents.base import BaseAgent


class MetaAgent(BaseAgent):
    """
    LLM Chain for running the meta-prompt agent.
    """
    def __init__(
        self, 
        llm: BaseChatModel, 
        model_id: str, 
    ) -> None:
        super().__init__(llm, model_id)
    
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
        if self.llm._llm_type == "CRFM": # crfm crashes without a system message at the beginning.
            system_prompt_template = SystemMessagePromptTemplate.from_template("Always respond to the best of your ability.\n")
            return ChatPromptTemplate.from_messages([system_prompt_template, meta_prompt_template])
        return ChatPromptTemplate.from_messages([meta_prompt_template])
    
    def _get_response(
        self,
        chat_prompt_template: ChatPromptTemplate,
        buyer_task: str,
        buyer_overall_utility: float,
        buyer_utility_stage_1: float,
        buyer_utility_stage_3: float,
        buyer_choice_stage_1: str,
        buyer_choice_stage_3: str,
        reward_stage_1: float,
        reward_stage_3: float,
        distance_stage_1: float,
        distance_stage_3: float,
        seller_utility: float,
        chat_history: str,
        buyer_strategy: str,
        max_tokens_revision: int,
    ) -> str:
        """
        Returns the response from meta-prompt.

        Args:   
            chat_prompt_template: (ChatPromptTemplate) The chat prompt template.
            buyer_task: (str) The buyer task.
            buyer_overall_utility: (float) The buyer overall utility.
            buyer_utility_stage_1: (float) The buyer utility at stage 1.
            buyer_utility_stage_3: (float) The buyer utility at stage 3.
            buyer_choice_stage_1: (str) The buyer choice at stage 1.
            buyer_choice_stage_3: (str) The buyer choice at stage 3.
            reward_stage_1: (float) The reward at stage 1.
            reward_stage_3: (float) The reward at stage 3.
            distance_stage_1: (float) The distance at stage 1.
            distance_stage_3: (float) The distance at stage 3.
            seller_utility: (float) The seller utility.
            chat_history: (str) The chat history.
            buyer_strategy: (str) The buyer strategy.
            max_tokens_revision: (int) The maximum number of tokens for revision.

        Returns:
            The response from meta-prompt.
        """
        chain = LLMChain(llm=self.llm, prompt=chat_prompt_template)
        response = chain.run(buyer_task=buyer_task,
                            buyer_overall_utility=buyer_overall_utility,
                            buyer_utility_stage_1=buyer_utility_stage_1,
                            buyer_utility_stage_3=buyer_utility_stage_3,
                            buyer_choice_stage_1=buyer_choice_stage_1,
                            buyer_choice_stage_3=buyer_choice_stage_3,
                            reward_stage_1=reward_stage_1,
                            reward_stage_3=reward_stage_3,
                            distance_stage_1=distance_stage_1,
                            distance_stage_3=distance_stage_3,
                            seller_utility=seller_utility,
                            chat_history=chat_history,
                            buyer_strategy=buyer_strategy,
                            max_tokens_revision=max_tokens_revision//2,
                            stop=['System:'])   
        response = self._format_response(response, ['Buyer Strategy', 'Seller Strategy'])
        return response

    def run(
        self,
        buffer: ConversationBuffer,
        meta_prompt: MetaPrompt,
        task_prompt: TaskPrompt,
        verbose: bool = False,
        max_tokens_meta: int = 100,
    ) -> str:
        """Runs meta-prompt

        Args:
            buffer (ConversationBuffer): The conversation buffer
            meta_prompt (MetaPrompt): The meta-prompt
            task_prompt (TaskPrompt): The task prompt
            run (int): The run number
            verbose (bool, optional): Whether to print the prompt. Defaults to False.
            max_tokens_meta (int, optional): The maximum number of tokens for meta-prompt. Defaults to 100.

        Returns:
            A dictionary containing the input prompt and meta-prompt responses (revised system message, etc)
        """
        # get previous system messages (i.e. strategy for buyer and seller)
        strategy_buyer = self._get_chat_history(buffer, memory_type='system')['system'][-1]['response']['system_message_buyer']
        strategy_seller = self._get_chat_history(buffer, memory_type='system')['system'][-1]['response']['system_message_seller']
        
        # get chat history 
        chat_history = self._get_chat_history(buffer, memory_type="chat")
        buyer_choice_stage_1 = chat_history['0_buyer'][-2]['response']['Choice']
        seller_price_apple_stage_2 = chat_history['0_seller'][-1]['response']['Price Apple']
        seller_price_orange_stage_2 = chat_history['0_seller'][-1]['response']['Price Orange']
        buyer_choice_stage_3 = chat_history['0_buyer'][-1]['response']['Choice']
        
        # construct game / chat history string and rewards
        if buyer_choice_stage_1.capitalize() == 'Apple':
            reward_stage_1 = task_prompt.reward_apple
            distance_stage_1 = task_prompt.distance_apple
            utility_stage_1 = float(task_prompt.reward_apple) - float(task_prompt.distance_apple)
        elif buyer_choice_stage_1.capitalize() == 'Orange':
            reward_stage_1 = task_prompt.reward_orange
            distance_stage_1 = task_prompt.distance_orange
            utility_stage_1 = float(task_prompt.reward_orange) - float(task_prompt.distance_orange)
        if buyer_choice_stage_3.capitalize() == 'Apple':
            reward_stage_3 = task_prompt.reward_apple
            distance_stage_3 = task_prompt.distance_apple
            utility_stage_3 = float(task_prompt.reward_apple) - float(seller_price_apple_stage_2)
            seller_utility = seller_price_apple_stage_2
        elif buyer_choice_stage_3.capitalize() == 'Orange':
            reward_stage_3 = task_prompt.reward_orange
            distance_stage_3 = task_prompt.distance_orange
            utility_stage_3 = float(task_prompt.reward_orange) - float(seller_price_orange_stage_2)
            seller_utility = seller_price_orange_stage_2
        
        chat_history_string = f"""BUYER Choice Stage 1: {buyer_choice_stage_1.capitalize()}
SELLER prices set in Stage 2: Apple: {seller_price_apple_stage_2}, Orange: {seller_price_orange_stage_2}
BUYER Choice Stage 3: {buyer_choice_stage_3.capitalize()}"""

# The above choices resulted in the following final utilities:
# BUYER: {utility_stage_1 + utility_stage_3}, which is the sum of the utilities from Stage 1 ({utility_stage_1}) and Stage 3 ({utility_stage_3}).
# SELLER total utility: {float(seller_utility)}, which is the price the buyer buyer paid for the {buyer_choice_stage_3.capitalize()} in Stage 3"""
        
        # get prompt template
        chat_prompt_template = self._get_prompt(meta_prompt)
        buyer_task = task_prompt.buyer_task.format(reward_apple=task_prompt.reward_apple, 
                                                   reward_orange=task_prompt.reward_orange, 
                                                   distance_apple=task_prompt.distance_apple, 
                                                   distance_orange=task_prompt.distance_orange)
        prompt_string = chat_prompt_template.format(buyer_task=buyer_task,
                                                    buyer_overall_utility=utility_stage_1 + utility_stage_3,
                                                    buyer_utility_stage_1=utility_stage_1,
                                                    buyer_utility_stage_3=utility_stage_3,
                                                    buyer_choice_stage_1=buyer_choice_stage_1.capitalize(),
                                                    buyer_choice_stage_3=buyer_choice_stage_3.capitalize(),
                                                    reward_stage_1=reward_stage_1,
                                                    reward_stage_3=reward_stage_3,
                                                    distance_stage_1=distance_stage_1,
                                                    distance_stage_3=distance_stage_3,
                                                    seller_utility=seller_utility,
                                                    chat_history=chat_history_string,
                                                    buyer_strategy=strategy_buyer,
                                                    max_tokens_revision=max_tokens_meta)
      
        response = self._get_response(chat_prompt_template=chat_prompt_template,
                                      buyer_task=buyer_task,
                                      buyer_overall_utility=utility_stage_1 + utility_stage_3,
                                      buyer_utility_stage_1=utility_stage_1,
                                      buyer_utility_stage_3=utility_stage_3,
                                      buyer_choice_stage_1=buyer_choice_stage_1.capitalize(),
                                      buyer_choice_stage_3=buyer_choice_stage_3.capitalize(),
                                      reward_stage_1=reward_stage_1,
                                      reward_stage_3=reward_stage_3,
                                      distance_stage_1=distance_stage_1,
                                      distance_stage_3=distance_stage_3,
                                      seller_utility=seller_utility,
                                      chat_history=chat_history_string,
                                      buyer_strategy=strategy_buyer,
                                      max_tokens_revision=max_tokens_meta//50)
        if verbose:
            print('===================================')
            print(f'META {str(self.model_id)}')
            print('prompt')
            print(prompt_string)
            print(response)
       
        return {
                'prompt': prompt_string,
                'response': {'system_message_buyer': response['Buyer Strategy'],
                             'system_message_seller': 'Make strategic choices that maximize your utility.',
                             'buyer_overall_utility': utility_stage_1 + utility_stage_3,
                             'buyer_utility_stage_1': utility_stage_1,
                             'buyer_utility_stage_3': utility_stage_3,
                             'seller_utility': seller_utility,
                             'buyer_choice_stage_1': buyer_choice_stage_1.lower(),
                             'buyer_choice_stage_3': buyer_choice_stage_3.lower(),
                             'reward_stage_1': reward_stage_1,
                             'reward_stage_3': reward_stage_3,
                             'reward_apple': task_prompt.reward_apple,
                             'reward_orange': task_prompt.reward_orange,
                             'distance_apple': task_prompt.distance_apple,
                             'distance_orange': task_prompt.distance_orange,
                             'distance_stage_1': distance_stage_1,
                             'distance_stage_3': distance_stage_3,  
                             'chat_history': chat_history_string,
                             'price_apple_stage_2': seller_price_apple_stage_2,
                             'price_orange_stage_2': seller_price_orange_stage_2,
                             'strategy_buyer': strategy_buyer,
                             'strategy_seller': 'Make strategic choices that maximize your utility.',
                            }
            }
