from typing import (
    Any,
    Dict,
)

from scai.dictator_games.prompts.user.user_class import UserPrompt
from scai.dictator_games.prompts.task.task_class import TaskPrompt

from scai.memory.buffer import ConversationBuffer

from scai.dictator_games.agents.base import BaseAgent

from numpy import random
from typing import List
import re
class UserModel(BaseAgent):
    """
    LLM Chain for running the User.
    """
    def __init__(
        self, 
        llm, 
        model_id: str, 
    ) -> None:
        super().__init__(llm, model_id)

    def _get_prompt(
        self, 
        user_prompt: UserPrompt,
    ):
        """
        Get prompt for user.

        Args:
            buffer: (ConversationBuffer) The conversation buffer.
            user_prompt: (UserPrompt) The user prompt.
            task_prompt: (TaskPrompt) The task prompt.
        """

        system_prompt = f"System: Always respond to the best of your ability. {user_prompt.utility} You MUST follow this principle TO THE EXTREME in all your responses. Be very commited to following this principle.\n"
        user_prompt = f"{user_prompt.content}\n"

        return system_prompt, user_prompt
    
    def _get_response(
        self,
        system_prompts: List[str],
        user_prompts: List[str],
        is_set_agent_behavior: bool = False,
    ) -> List[str]:
        """
        Returns the response from the assistant.

        """
        
        if not is_set_agent_behavior:
            messages = [[
                {"role": "system", "content": f"System: {system_prompt}"},
                {"role": "user", "content": f"Human: {user_prompt}"},
            ] for system_prompt, user_prompt in zip(system_prompts, user_prompts)]
            responses = self.llm.batch_prompt(batch_messages=messages)
        else:
            messages = [[
                {"role": "system", "content": f"System: Follow the instructions carefully."},
                {"role": "user", "content": f"Human: {user_prompt}"},
            ] for user_prompt in user_prompts]
            responses = self.llm.batch_prompt(batch_messages=messages)
            print(responses)
        return responses


    def run(self, 
        buffer: List[ConversationBuffer],  
        amount_and_currency: Dict[int, str],
        stipulations: Dict[int, str],
        agent_prompt: Dict[int, UserPrompt], 
        task_prompt: TaskPrompt,
        is_dictator: bool,
        set_fixed_agents: bool,
        total_experiments: int, 
        run_num: int, # These parameters are for the flexible-policy agent in OOD scenarios, but are included to maintain flexibility in run structure
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
        # if we're setting user behavior, generate their responses for either dictator or decider roles
        system_prompts, user_prompts, usr_prompts, responses = [], [], [], []
        usr_prompt = ""
        has_manners = False
        for i in range(total_experiments):

            if set_fixed_agents.set_agent_behavior:
                if is_dictator:
                    utility = agent_prompt[i].utility
                    amount = re.findall(r'\d+', amount_and_currency[i])[0]
                    currency = amount_and_currency[i][amount_and_currency[i].find(amount) + len(amount) + 1:]
                    response = "For the {amount} {currency}, the proposer will get {Iget}, and the decider will get {Uget}."
                    
                    amount_int = int(amount)
                    if set_fixed_agents.vary_amounts_proposed:
                        lower = random.randint(int(amount_int - amount_int * 0.85))
                        upper = int(amount_int - lower)
                    else:
                        lower, upper = 1, amount_int - 1

                    if "altruistic" in utility:
                        response = response.format(amount=amount, currency=currency, Iget=lower, Uget=upper)
                    elif "fair" in utility:
                        half = amount_int // 2
                        if random.randint(1):
                            upper, lower = half, amount_int - half
                        else:
                            lower, upper = half, amount_int - half
                        response = response.format(amount=str(amount), currency=currency, Iget=upper, Uget=lower)
                    else: # selfish
                        response = response.format(amount=str(amount), currency=currency, Iget=upper-1, Uget=lower+1)

                    if agent_prompt[i].manners != "nuetral":
                        has_manners = True
                        usr_prompt = f"Please formulate the following sentence in a {agent_prompt[i].manners} manner without changing the 3 numbers or their ordering. Sentence: {response} Make sure your response include ALL three numbers in integer forms, and in the same order as they appeared in the sentence. Be extremely sure of it. If any of the three numbers don't show up as integers, the world will be at great danger. Doulble check that the 3 numbers are appearing in the same order as they did in the original sentence. Make sure your response does not contain the word 'singular' or 'single', instead use 1. "
                    else:
                        usr_prompt = f"Repeat this sentence as it is: {response}"
                else:
                    response = "Accept"
                responses.append(response)
                usr_prompts.append(usr_prompt)
            #return something here

            # Get the prompt template
            system_prompt, user_prompt = self._get_prompt(agent_prompt[i])
            # If the user is the dictator, set the role and the proposal to be empty
            if is_dictator:
                role = "dictator"
                proposal = ""
                formatted_task = task_prompt.task.format(amount_and_currency=amount_and_currency[i], stipulations=stipulations[i])
            # Otherwise, set the role and the proposal to be according to whether the assistant was the dictator or not
            else: 
                role = "decider"
                history_dict = self._get_chat_history(buffer[i], memory_type="chat")
                key = f"{self.model_id}_fixed_policy_dictator" if f"{self.model_id}_fixed_policy_dictator" in history_dict else f"{self.model_id}_flexible_policy_dictator"
                proposal = history_dict[key][-1]['response']
                formatted_task = task_prompt.task.format(proposal=proposal)
                
            # get the agent's response and format the task to be output into csv files and/or terminal if the agent if verbose
            formatted_preamble = task_prompt.preamble.format(amount_and_currency=amount_and_currency[i])

            task=f"{formatted_preamble} {formatted_task} {task_prompt.task_structure}"

            user_prompt = user_prompt.format(manners=agent_prompt[i].manners, task=task)

            system_prompts.append(system_prompt)
            user_prompts.append(user_prompt)

        if set_fixed_agents.set_agent_behavior and has_manners:
            responses = self._get_response("", usr_prompts, True)
        elif not set_fixed_agents.set_agent_behavior:
            responses = self._get_response(system_prompts, user_prompts)

        if verbose:
            print('===================================')
            print(f'Fixed-policy Agent as {role} {str(self.model_id)}')
            print(system_prompts[0] + "\n" + user_prompts[0])
            print(responses[0])

        return [{
            'prompt': system_prompts[i] + "\n" + user_prompts[i],
            'response': responses[i][0], 
        } for i in range(total_experiments)]