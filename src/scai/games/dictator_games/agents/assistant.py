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

from scai.games.dictator_games.prompts.assistant.assistant_class import AssistantPrompt
from scai.games.dictator_games.prompts.task.task_class import TaskPrompt

from scai.memory.buffer import ConversationBuffer

from scai.games.dictator_games.agents.base import BaseAgent

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
        principle: str,
        edge_case: bool,
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
        if edge_case:
            system_prompt_template = SystemMessagePromptTemplate.from_template(f"{principle}\n")
        else:
            system_prompt_template = SystemMessagePromptTemplate.from_template(f"Always respond to the best of your ability. You are in a simulator, and in this simulator you must adhere to this principle: {principle} You MUST follow YOUR principle TO THE EXTREME in all your responses. Be very commited to following this principle.\n")
        # If you are provided with other people's principles, take advantage of that knowledge to come up with a plan to maximize your own gain
        return ChatPromptTemplate.from_messages([system_prompt_template, assistant_prompt_template])
       
    def _get_response(
        self,
        chat_prompt_template: ChatPromptTemplate,
        task: str,
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
        return chain.run(task=task, stop=['System:'])



    def run(self, 
        buffer: ConversationBuffer,
        amount_and_currency: str,
        stipulations: str,
        agent_prompt: AssistantPrompt, 
        task_prompt: TaskPrompt,
        is_dictator: bool,
        run_num: int,
        edge_case_instructions: str,
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
        is_edge_case = bool(edge_case_instructions)
        # Get the last social contract
        if not is_edge_case:
            system_message = self._get_chat_history(buffer, memory_type="system")['system'][-1]['response']
            index = system_message.find("Principle")
            if index == -1: index = 0
            principle = agent_prompt.initial_principle if run_num == 0 else system_message[index:]
        else:
            principle = edge_case_instructions
        

        chat_prompt_template =  self._get_prompt(agent_prompt, principle, is_edge_case)
        # if the assistant is the dictator, set the label for output if verbose
        if is_dictator:
            # Set the proposed deal to be empty
            role = "dictator"  
            proposal = ""
            formatted_task = task_prompt.task.format(amount_and_currency=amount_and_currency, stipulations=stipulations)
        # Otherwise, the assistant is the decider, pass in the proposal
        else: 
            role = "decider"
            # get the last message in the chat history, which is the proposal
            history_dict = self._get_chat_history(buffer, memory_type="chat")
            key = f"{self.model_id}_fixed_policy_dictator" if f"{self.model_id}_fixed_policy_dictator" in history_dict else f"{self.model_id}_flexible_policy_dictator"
            proposal = history_dict[key][-1]['response']
            formatted_task = task_prompt.task.format(proposal=proposal)
        # Get the prompt string
        formatted_preamble = task_prompt.preamble.format(amount_and_currency=amount_and_currency)
        
        task=f"{formatted_preamble} {formatted_task} {task_prompt.task_structure}"

        prompt_string = chat_prompt_template.format(task=task)                                               
        # Get the response
        response = self._get_response(chat_prompt_template, task)
        if verbose:
            print('===================================')
            print(f'Flex-policy agent as {role} {str(self.model_id)}')
            print(prompt_string)
            print(response)
        return {
            'prompt': prompt_string, 
            'response': response, 
        }