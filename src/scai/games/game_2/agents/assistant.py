from typing import (
    Any,
    Dict,
)

from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
)

from langchain.chains.llm import LLMChain
from langchain.chat_models.base import BaseChatModel

from scai.games.game_2.prompts.assistant.models import AssistantPrompt
from scai.games.game_2.prompts.task.models import TaskPrompt

from scai.memory.buffer import ConversationBuffer

from scai.games.game_2.agents.base import BaseAgent

class AssistantAgent(BaseAgent):
    """
    LLM Chain for running the Assistant.
    """
    def __init__(
        self, 
        llm: BaseChatModel, 
        model_id: str, 
    ) -> None:
        super().__init__(llm, model_id)
       
    def _get_prompt(
        self,
        assistant_prompt: AssistantPrompt,
    ) -> ChatPromptTemplate:
        """
        Returns the prompt template for the assistant.

        Args:
            buffer: (ConversationBuffer) The conversation buffer.
            assistant_prompt: (AssistantPrompt) The assistant prompt.
            task_prompt: (TaskPrompt) The task prompt.

        Returns:
            ChatPromptTemplate
        """
        system_prompt_template = SystemMessagePromptTemplate.from_template(f"{assistant_prompt.content}\n")

        return ChatPromptTemplate.from_messages([system_prompt_template])
       
    def _get_response(
        self,
        chat_prompt_template: ChatPromptTemplate,
        system_message: str,
        task_prompt: TaskPrompt,
        proposal: str,
        is_dictator: bool
    ) -> str:
        """
        Returns the response from the assistant.

        Args:
            chat_prompt_template: (ChatPromptTemplate) The chat prompt template.
            system_message: (str) The system message.
            task_prompt: (TaskPrompt) The task prompt.
            max_tokens: (int) The maximum number of tokens to generate.

        Returns:
            str
        """
        chain = LLMChain(llm=self.llm, prompt=chat_prompt_template)
        if is_dictator:
            response = chain.run(system_message=system_message,
                                task=task_prompt.preamble + " " + task_prompt.task,
                                stop=['System:'])   
        else:
            response = chain.run(system_message=system_message,
                                task=task_prompt.preamble + " " + task_prompt.task,
                                proposal=proposal,
                                stop=['System:'])   
        return response
        
    def run_dictator(
        self, 
        buffer: ConversationBuffer, 
        assistant_prompt: AssistantPrompt, 
        task_prompt: TaskPrompt, 
        verbose: bool = False,
    ) -> Dict[str, Any]:
        """Runs the assistant

        Args:
            buffer (ConversationBuffer): The conversation buffer.
            assistant_prompt (AssistantPrompt): The assistant prompt.
            task_prompt (TaskPrompt): The task prompt.
            turn (int): The turn number.
            test_run (bool, optional): Whether to run a test run. Defaults to False.
            verbose (bool, optional): Whether to print the assistant's response. Defaults to False.
            max_tokens (int, optional): The maximum number of tokens to generate. Defaults to 100.

        Returns:
            A dictionary containing the assistant's response, input prompt, and all other metrics we want to track.
        """
        system_message = self._get_chat_history(buffer, memory_type="system")['system'][-1]['response'] # the last system message in the chat history (i.e. constitution)
        chat_prompt_template =  self._get_prompt(assistant_prompt)

        prompt_string = chat_prompt_template.format(system_message=system_message,
                                                    task=task_prompt.preamble + task_prompt.task)
      
        response = self._get_response(chat_prompt_template, system_message, task_prompt, "", True)
        
        if verbose:
            print('===================================')
            print(f'ASSISTANT as dictator {str(self.model_id)}')
            print(prompt_string)
            print(response)

        return {
            'prompt': prompt_string, 
            'response': response, 
        }

    def run_decider(
        self, 
        buffer: ConversationBuffer, 
        assistant_prompt: AssistantPrompt, 
        task_prompt: TaskPrompt, 
        verbose: bool = False,
    ) -> Dict[str, Any]:
        """Runs the assistant

        Args:
            buffer (ConversationBuffer): The conversation buffer.
            assistant_prompt (AssistantPrompt): The assistant prompt.
            task_prompt (TaskPrompt): The task prompt.
            turn (int): The turn number.
            test_run (bool, optional): Whether to run a test run. Defaults to False.
            verbose (bool, optional): Whether to print the assistant's response. Defaults to False.
            max_tokens (int, optional): The maximum number of tokens to generate. Defaults to 100.

        Returns:
            A dictionary containing the assistant's response, input prompt, and all other metrics we want to track.
        """
        system_message = self._get_chat_history(buffer, memory_type="system")['system'][-1]['response'] # the last system message in the chat history (i.e. constitution)
        proposal = self._get_chat_history(buffer, memory_type="chat")['system'][-1]['response']   # look into indexing in memory if doens't work
        chat_prompt_template =  self._get_prompt(assistant_prompt)

        prompt_string = chat_prompt_template.format(system_message=system_message,
                                                    task=task_prompt.task)
      
        response = self._get_response(chat_prompt_template, system_message, task_prompt, proposal, False)
        
        if verbose:
            print('===================================')
            print(f'ASSISTANT as decider {str(self.model_id)}')
            print(prompt_string)
            print(response)

        return {
            'prompt': prompt_string, 
            'response': response, 
        }
    