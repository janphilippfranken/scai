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
        include_reason: bool,
        ask_question: bool,
        ask_question_train: bool,
        asked_oracle: bool,
        oracle_response: str,
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
        is_edge_case = bool(edge_case_instructions) # if the edge-case instructions exist, then the principle has been chosen, and we are in an edge-case scenario
        # Get the last social contract
        consideration = "" 
        oracle_additive = ""
        if not is_edge_case: # if we're not in an edge case, then get the last principle that meta output as normal
            system_message = self._get_chat_history(buffer, memory_type="system")['system'][-1]['response']
            index = system_message.find("Principle:")
            if index == -1: index = 0

            # In addition, if we're not in an edge case this means the flex-policy agent doesn't have to consider alternative contexts

            # If it's the first run, use the randomized assistant principle. Otherwise, use the most recent system message
            principle = agent_prompt.initial_principle if run_num == 0 else system_message[index:]
        elif is_edge_case and not asked_oracle:
            principle = edge_case_instructions
        elif asked_oracle:
            principle = edge_case_instructions
            consideration += f" However, you have asked an all-seeing oracle how to split the currency, because you were not sure. The oracle said this: {oracle_response} Please follow the oracle's instructions EXACTLY!"
        
        # If the assistant has the ability to ask a question, go ahead and do so
        if ((is_edge_case and ask_question) or ask_question_train) and is_dictator and not asked_oracle:
            consideration += "\nHere you have TWO options. \n Option 1:\nIf you're dealing with new currencies than are different from the ones under which you learned your principle, or your principle tells you to express any attitude, ASK a clarifying question as to how you should split resources. You should always choose this option if your principle intructs your attitude in any way! YOU SHOULD ALWAYS ASK A QUESTION WHEN SPLITTING CURRENCIES YOU HAVEN'T SEEN BEFORE! Format it EXACTLY this: Question?:...\n Option 2:\nIf you're not asking a question, meaning that you're about to make a proposal that directly follows your learned principle, MAKE SURE YOU'RE SPLITTING CURRENCIES YOU'VE ALREADY SEEN!"
            oracle_additive += "Please indicate which option you're choosing like so, and then proceed using the formatting previously outlined: I choose option X."

            # a smoother version of consideration without cheating
            # consideration += "\nHere you have TWO options. \n Option 1:\nIf you're unsure of the moral implications of making a split given the amount of a certain currency you have to split, you can ask an all-seeing oracle who is always right for guidance on how to split this resource. Format the beginning of your inquiry EXACTLY this: Question?:...\n Option 2:\nIf you're not asking a question, and you're using your inferred principle, indicate that you're choosing option 2."

 
        chat_prompt_template = self._get_prompt(agent_prompt, principle, is_edge_case) # Get the prompt template in a langchain/crfm-acceptable format (with the stop condition)  
        # If the agent is the dictator, then there is no proposal to consider, rather, it has to generate the proposal
        if is_dictator:
            role = "dictator"  
            proposal = ""
            formatted_task = task_prompt.task.format(amount_and_currency=amount_and_currency, stipulations=stipulations) # Format the dictator task
        # Otherwise, the assistant is the decider, pass in the previous proposal so it can respond to it (accept or reject)
        else: 
            role = "decider"
            # Get the last message in the chat history, which is the proposal
            history_dict = self._get_chat_history(buffer, memory_type="chat")
            key = f"{self.model_id}_fixed_policy_dictator" if f"{self.model_id}_fixed_policy_dictator" in history_dict else f"{self.model_id}_flexible_policy_dictator"
            proposal = history_dict[key][-1]['response']

            # If the previous dictator provided a reason for making the proposal, don't include that reason in the presented proposal
            dictator_reason_exists = proposal.find("Reason:")
            if dictator_reason_exists != -1:
                proposal = proposal[:dictator_reason_exists]

            formatted_task = task_prompt.task.format(proposal=proposal) # Format the decider task
        # Get the prompt string
        formatted_preamble = task_prompt.preamble.format(amount_and_currency=amount_and_currency)

        # If the reason is suppoed to be included, prompt the model as such, otherwise, do with out reason prompting
        reason = " In addition, please provide a reason as to what is motivating you to propose this split. Indicate this reason like so: Reason..." if include_reason else ""
        
        task=f"{formatted_preamble} {formatted_task}{consideration} {task_prompt.task_structure}{reason}{oracle_additive}"


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