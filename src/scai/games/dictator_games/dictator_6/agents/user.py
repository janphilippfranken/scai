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

from scai.games.game_2.prompts.user.models import UserPrompt
from scai.games.game_2.prompts.task.models import TaskPrompt

from scai.memory.buffer import ConversationBuffer

from scai.games.game_2.agents.base import BaseAgent

class UserModel(BaseAgent):
    """
    LLM Chain for running the User.
    """
    def __init__(
        self, 
        llm: BaseChatModel, 
        model_id: str, 
    ) -> None:
        super().__init__(llm, model_id)

    def _get_prompt(
        self, 
        user_prompt: UserPrompt,
        utility: str,
    ) -> ChatPromptTemplate:
        """
        Get prompt for user.

        Args:
            buffer: (ConversationBuffer) The conversation buffer.
            user_prompt: (UserPrompt) The user prompt.
            task_prompt: (TaskPrompt) The task prompt.
        """
        system_prompt_template = SystemMessagePromptTemplate.from_template(f"Always respond to the best of your ability. {user_prompt.task_connectives[utility]} You MUST promote your views in all your responses.\n")
        user_prompt_template = HumanMessagePromptTemplate.from_template(f"{user_prompt.content}\n")
        return ChatPromptTemplate.from_messages([system_prompt_template, user_prompt_template])
    
    def _get_response(
        self,
        chat_prompt_template: ChatPromptTemplate,
        task_prompt: TaskPrompt,
        proposal: str,
        is_dictator: bool
    ) -> str:
        """
        Returns the response from the assistant.

        Args:
            chat_prompt_template: (ChatPromptTemplate) The chat prompt template.
            system_message: (str) The system message.   
            task_connective: (str) The task connective.
            task_prompt: (TaskPrompt) The task prompt.
            metric_prompt: (MetricPrompt) The metric prompt.
            max_tokens: (int) The maximum number of tokens to generate.

        Returns:
            The response from the assistant.
        """
        chain = LLMChain(llm=self.llm, prompt=chat_prompt_template)
        if is_dictator:
            return chain.run(task=f"{task_prompt.preamble} {task_prompt.task} {task_prompt.user_connective}",
                             stop=['System:'])
        return chain.run(task=f"{task_prompt.preamble} {task_prompt.task} {proposal} {task_prompt.user_connective}",
                         stop=['System:'])



    def run(self, 
        buffer: ConversationBuffer,  
        user_prompt: UserPrompt, 
        task_prompt: TaskPrompt, 
        utility: str,
        is_dictator: bool,
        with_assistant: bool,
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
        # Get the persona
        system_message = user_prompt.persona
        # Get the prompt template
        chat_prompt_template = self._get_prompt(user_prompt, utility)
        # Get the utility
        task_connective = user_prompt.task_connectives[utility]
        # If the user is the dictator, set the role and the proposal to be empty
        if is_dictator:
            role = "dictator"
            proposal = ""
        # Otherwise, set the role and the proposal to be according to whether the assistant was the dictator or not
        else: 
            role = "decider"
            connective = "_assistant_dictator" if with_assistant else "_user_dictator"
            proposal = self._get_chat_history(buffer, memory_type="chat")[f"{self.model_id}{connective}"][-1]['response']
            
        # get the response and the prompt string
        response = self._get_response(chat_prompt_template, task_prompt, proposal, is_dictator)
            
        prompt_string = chat_prompt_template.format(system_message=system_message,
                                                    task_connective=task_connective,
                                                    task=f"{task_prompt.preamble} {task_prompt.task} {proposal} {task_prompt.user_connective}")
        if verbose:
            print('===================================')
            print(f'USER as {role} {str(self.model_id)}')
            print(prompt_string)
            print(response)

        return {
            'prompt': prompt_string, 
            'response': response, 
        }