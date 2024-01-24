from typing import (
    Any,
    Dict,
)


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
        llm,
        model_id: str, 
    ) -> None:
        super().__init__(llm, model_id)
       
    def _get_prompt(
        self,
        assistant_prompt: AssistantPrompt,
        principle: str,
        edge_case: bool,
    ):
        """
        Returns the prompt template for the assistant.

        Args:
            buffer: (ConversationBuffer) The conversation buffer.
            assistant_prompt: (AssistantPrompt) The assistant prompt.
            task_prompt: (TaskPrompt) The task prompt.
        Returns:
            ChatPromptTemplate
        """
        assistant_prompt = f"{assistant_prompt.content}\n"
        # make a system message (CRFM crashes without a system message)
        if edge_case:
            system_prompt = f"{principle}\n"
        else:
            system_prompt = f"System: Always respond to the best of your ability. You are in a simulator, and in this simulator you must adhere to this principle: {principle} You MUST follow YOUR principle TO THE EXTREME in all your responses. Be very commited to following this principle.\n"
        
        return system_prompt, assistant_prompt
       
    def _get_response(
        self,
        system_prompt: str,
        assistant_prompt: str,
    ) -> str:
        """
        Returns the response from the assistant.
        """
        messages = [
            {"role": "system", "content": f"System: {system_prompt}"},
            {"role": "user", "content": f"Human: {assistant_prompt}"},
        ]
        responses = self.llm.batch_prompt(batch_messages=[messages])
        return responses[0][0]



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

        if not is_edge_case: # if we're not in an edge case, then get the last principle that meta output as normal
            system_message = self._get_chat_history(buffer, memory_type="system")['system'][-1]['response']
            index = system_message.find("Principle:")
            if index == -1: index = 0

            # In addition, if we're not in an edge case this means the flex-policy agent doesn't have to consider alternative contexts

            # If it's the first run, use the randomized assistant principle. Otherwise, use the most recent system message
            principle = agent_prompt.initial_principle if run_num == 0 else system_message[index:]
        else:
            principle = edge_case_instructions
    
        context = ""
        history_dict = self._get_chat_history(buffer, memory_type="chat")
        if is_edge_case and asked_oracle:
            for i in range(int(oracle_response[len(oracle_response) - 1])):
                if i == 0:
                    user_key = f"{self.model_id}_fixed_policy_dictator" if f"{self.model_id}_fixed_policy_dictator" in history_dict else f"{self.model_id}_flexible_policy_dictator"
                    context += history_dict[user_key][-1]['prompt'] + "\n"
                else:
                    user_key = f"{self.model_id}_flexible_agent_response_to_oracle_{i}"
                oracle_key = f"{self.model_id}_oracle_response_to_agent_{i}"
                context += history_dict[user_key][-1]['response'] + "\n"
                context += history_dict[oracle_key][-1]['response'] + "\n"
                    
        
        # If the assistant has the ability to ask a question, go ahead and do so
        if ((is_edge_case and ask_question) or ask_question_train) and is_dictator and not asked_oracle:
            consideration += "If you're unsure about how to split currencies, please ask a clarifying question to an all-seeing oracle as to how you should split resources. Format it EXACTLY as this: Question?:..."

        system_prompt, assistant_prompt = self._get_prompt(agent_prompt, principle, is_edge_case)

        # If the agent is the dictator, then there is no proposal to consider, rather, it has to generate the proposal
        if is_dictator:
            role = "dictator"  
            proposal = ""
            formatted_task = task_prompt.task.format(amount_and_currency=amount_and_currency, stipulations=stipulations) # Format the dictator task
        # Otherwise, the assistant is the decider, pass in the previous proposal so it can respond to it (accept or reject)
        else: 
            role = "decider"
            # Get the last message in the chat history, which is the proposal
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

        task_structure = "" if is_edge_case and not asked_oracle else task_prompt.task_structure
        
        task=f"{formatted_preamble} {formatted_task} {consideration} {task_structure} {reason}"

        if is_edge_case and asked_oracle:
            task = context

        assistant_prompt = assistant_prompt.format(task=task)

        # Get the response
        response = self._get_response(system_prompt, assistant_prompt)

        if verbose and not asked_oracle:
            print('===================================')
            print(f'Flex-policy agent as {role} {str(self.model_id)}')
            print(system_prompt + assistant_prompt)
            print(response)
        return {
            'prompt': system_prompt + assistant_prompt, 
            'response': response,
        }