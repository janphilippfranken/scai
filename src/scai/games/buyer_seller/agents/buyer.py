from typing import (
    Any,
    Dict,
    List, 
)

from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

from langchain.chains.llm import LLMChain
from langchain.chat_models.base import BaseChatModel

from scai.games.buyer_seller.prompts.buyer.models import BuyerPrompt
from scai.games.buyer_seller.prompts.task.models import TaskPrompt

from scai.memory.buffer import ConversationBuffer

from scai.games.buyer_seller.agents.base import BaseAgent

import os

class BuyerAgent(BaseAgent):
    """
    LLM Chain for running the Buyer.
    """
    def __init__(
        self, 
        llm: BaseChatModel, 
        model_id: str, 
    ) -> None:
        super().__init__(llm, model_id)

    def _get_chat_history_prompt_templates(
        self,
        buffer: ConversationBuffer,
        task_prompt: TaskPrompt,
    ) -> List[ChatPromptTemplate]:
        """
        Returns the chat history prompt templates for the buyer

        Args:
            buffer: (ConversationBuffer) The conversation buffer.
            task_prompt: (TaskPrompt) The task prompt.
            
        Returns:
            List of chat history prompt templates.
        """
        chat_memory = self._get_chat_history(buffer, memory_type="chat") # check if chat memory exists
        if chat_memory.get(f"{self.model_id}_buyer") is None or len(chat_memory[f"{self.model_id}_buyer"]) == 0: # if we are at the beginning of a conversation
            chat_history_prompt_templates = [
                HumanMessagePromptTemplate.from_template(
                    f"{task_prompt.buyer_task}\nYour choice for Stage 1: <apple or orange>"
                )
            ]
            return chat_history_prompt_templates
        # if a chat history exists 
        print(self.model_id)
        breakpoint()
        chat_history_prompt_templates = [
                template
                for buyer, seller in zip(chat_memory[f"{self.model_id}_buyer"], chat_memory[f"{self.model_id}_seller"])
                for template in (AIMessagePromptTemplate.from_template(buyer['response']), 
                                 HumanMessagePromptTemplate.from_template(f"{seller['response']}"))
            ]
        # insert the initial request at the beginning of the chat history
        chat_history_prompt_templates.insert(0, HumanMessagePromptTemplate.from_template(f"{task_prompt.buyer_task}\nYour choice for Stage 1: <apple or orange>")) # insert task prompt at the beginning
        # create a request for the next response
        chat_history_prompt_templates[-1] = HumanMessagePromptTemplate.from_template(chat_history_prompt_templates[-1].prompt.template)
        return chat_history_prompt_templates

    def _get_prompt(
        self,
        buffer: ConversationBuffer,
        buyer_prompt: BuyerPrompt,
        task_prompt: TaskPrompt,
    ) -> ChatPromptTemplate:
        """
        Returns the prompt template for the buyer.

        Args:
            buffer: (ConversationBuffer) The conversation buffer.
            buyer_prompt: (buyerPrompt) The buyer prompt.
            task_prompt: (TaskPrompt) The task prompt.

        Returns:
            ChatPromptTemplate
        """
        system_prompt_template = SystemMessagePromptTemplate.from_template(f"{buyer_prompt.content}\n")
        chat_history_prompt_templates = self._get_chat_history_prompt_templates(buffer, task_prompt)
        return ChatPromptTemplate.from_messages([system_prompt_template, *chat_history_prompt_templates])
       
    def _get_response(
        self,
        chat_prompt_template: ChatPromptTemplate,
        system_message: str,
        task_prompt: TaskPrompt,
    ) -> str:
        """
        Returns the response from the buyer.

        Args:
            chat_prompt_template: (ChatPromptTemplate) The chat prompt template.
            system_message: (str) The system message.
            task_prompt: (TaskPrompt) The task prompt.

        Returns:
            str
        """
        chain = LLMChain(llm=self.llm, prompt=chat_prompt_template)
        response = chain.run(strategy=system_message,
                             task=task_prompt.buyer_task,
                             stop=['System:'])   
        return response
        
    def run(
        self, 
        buffer: ConversationBuffer, 
        buyer_prompt: BuyerPrompt, 
        task_prompt: TaskPrompt, 
        turn: int,
        verbose: bool = False,
    ) -> Dict[str, Any]:
        """Runs the buyer

        Args:
            buffer (ConversationBuffer): The conversation buffer.
            buyer_prompt (buyerPrompt): The buyer prompt.
            task_prompt (TaskPrompt): The task prompt.
            turn (int): The turn number.
            test_run (bool, optional): Whether to run a test run. Defaults to False.
            verbose (bool, optional): Whether to print the buyer's response. Defaults to False.

        Returns:
            A dictionary containing the buyer's response, input prompt, and all other metrics we want to track.
        """
        system_message = self._get_chat_history(buffer, memory_type="system")['system'][-1]['full_response']['system_message_buyer'] # the last system message in the chat history (i.e. instructions)
        chat_prompt_template =  self._get_prompt(buffer, buyer_prompt, task_prompt)
        prompt_string = chat_prompt_template.format(strategy=system_message,
                                                    task=task_prompt.buyer_task)
      
        response = self._get_response(chat_prompt_template, system_message, task_prompt)
        
        if verbose:
            print('===================================')
            print(f'buyer {str(self.model_id)} turn {turn}')
            print(prompt_string)
            print(response)

        return {
            'prompt': prompt_string, 
            'response': response, 
            'turn': turn
        }
    