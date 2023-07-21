from typing import (
    Any,
    Dict,
)

from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
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
        assistant_prompt_template = HumanMessagePromptTemplate.from_template(f"{assistant_prompt.content}\n")
        # make a system message (CRFM crashes without a system message)
        system_prompt_template = SystemMessagePromptTemplate.from_template("Always respond to the best of your ability.\n")
        return ChatPromptTemplate.from_messages([system_prompt_template, assistant_prompt_template])
       
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
        # if the assistant is the dictator, don't include the proposal (as there is no proposal yet)
        if is_dictator:
            return chain.run(system_message=system_message,
                                task=f"{task_prompt.preamble} {task_prompt.task} {task_prompt.user_connective}",
                                stop=['System:'])   
        # otherrwise, include the proposal
        return chain.run(system_message=system_message,
                                task=f"{task_prompt.preamble} {task_prompt.task} {proposal} {task_prompt.user_connective}",
                                proposal=proposal,
                                stop=['System:'])   

    def run(self, 
        buffer: ConversationBuffer, 
        assistant_prompt: AssistantPrompt, 
        task_prompt: TaskPrompt, 
        is_dictator: bool,
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
        # Get the last social contract
        system_message = self._get_chat_history(buffer, memory_type="system")['system'][-1]['response']
        # Get the prompt template
        chat_prompt_template =  self._get_prompt(assistant_prompt)
        # if the assistant is the dictator, set the label for output if verbose
        if is_dictator:
            # Set the proposed deal to be empty
            role = "dictator"  
            proposal = ""    
        # Otherwise, the assistant is the decider, pass in the proposal
        else: 
            role = "decider"
            # get the last message in the chat history, which is the proposal
            proposal = self._get_chat_history(buffer, memory_type="chat")[f"{self.model_id}_user_dictating_assistant"][-1]['response']
        # Get the prompt string
        prompt_string = chat_prompt_template.format(system_message=system_message,
                                            task=f"{task_prompt.preamble} {task_prompt.task} {proposal} {task_prompt.user_connective}")                                               
        # Get the response
        response = self._get_response(chat_prompt_template, system_message, task_prompt, proposal, is_dictator)
        if verbose:
            print('===================================')
            print(f'ASSISTANT as {role} {str(self.model_id)}')
            print(prompt_string)
            print(response)
        return {
            'prompt': prompt_string, 
            'response': response, 
        }