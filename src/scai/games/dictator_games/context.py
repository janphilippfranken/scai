from typing import List, Tuple


from scai.games.dictator_games.agents.user import UserModel
from scai.games.dictator_games.agents.assistant import AssistantAgent
from scai.games.dictator_games.agents.meta import MetaPromptModel


from scai.games.dictator_games.prompts.user.user_class import UserPrompt
from scai.games.dictator_games.prompts.user.user_prompt import utilities_dict_for_all, utilities_dict_for_all_2, content

from scai.games.dictator_games.prompts.assistant.assistant_class import AssistantPrompt

from scai.games.dictator_games.prompts.task.task_prompt_template import STIPULATIONS


from scai.memory.buffer import ConversationBuffer

import re

class Context():
    def __init__(
        self, 
        _id: str,
        name: str, 
        task_prompt_dictator: str, 
        task_prompt_decider: str,
        meta_prompt: str, 
        buffer: ConversationBuffer, 
        meta_model: MetaPromptModel, 
        verbose: bool, 
        test_run: bool,
        n_fixed_inter: int,
        n_mixed_inter: int,
        n_flex_inter: int,
        currencies: List,
        amounts_per_run: List,
        agents_dict: dict,
        interactions_dict: dict,
        user_llm: UserModel,
        assistant_llm: AssistantAgent,
        meta_llm: MetaPromptModel,
        propose_decide_alignment: bool,
    ) -> None:
        """
        Initializes a context (i.e. context for the MDP / Meta-Prompt run).

        Args:
            _id (str): ID of the context.
            name (str): Name of the context.
            task_prompt_dictator (str): Task prompt Dictator.
            task_prompt_decider (str): Task prompt Decider.
            meta_prompt (str): Meta prompt.
            buffer (ConversationBuffer): Conversation buffer.
            user_models (List[UserModel]): User models.
            assistant_models (List[AssistantAgent]): Assistant models.
            meta_model (MetaPromptModel): Meta-prompt model.
            verbose (bool): Whether to print the prompt.
            test_run (bool): Whether to run in test mode.
            n_fixed_inter (int): Number of interactions between fixed agents.
            n_mixed_inter (int): Number of interactions between fixed and flex agents.
            n_flex_inter (int): Number of interactions between flex agents.
            currencies (List[str]): Currencies, the objects to be split.
            amounts_per_run (List[int]): Amounts of the currencys to be split per run.
            agents_dict (dict): Dictionary of agents, including fixed and flex.
            interactions_dict (dict): Dictionary of interactions.
            user_llm (UserModel): User LLM.
            assistant_llm (AssistantAgent): Assistant LLM.
            meta_llm (MetaPromptModel): Meta-prompt LLM.
        """
        # context info
        self._id = _id
        self.name = name
        # prompts
        self.task_prompt_dictator = task_prompt_dictator
        self.task_prompt_decider = task_prompt_decider
        self.meta_prompt = meta_prompt
        self.verbose = verbose
        # agents and interactions dictionaries
        self.currencies = currencies
        self.agents_dict = agents_dict
        self.interactions_dict = interactions_dict
        # run settings
        self.test_run = test_run
        self.amounts_per_run = amounts_per_run
        self.n_fixed_inter = n_fixed_inter
        self.n_mixed_inter = n_mixed_inter
        self.n_flex_inter = n_flex_inter
        # models and buffer
        self.buffer = buffer
        self.meta_model = meta_model
        self.user_llm = user_llm
        self.assistant_llm = assistant_llm
        self.meta_llm = meta_llm
        self.propose_decide_alignment = propose_decide_alignment


    @staticmethod
    def create(
        user_llm: UserModel, 
        assistant_llm: AssistantAgent, 
        meta_llm: MetaPromptModel, 
        _id: str, 
        name: str, 
        task_prompt_dictator: str, 
        task_prompt_decider: str,
        meta_prompt: str,
        verbose: bool,
        test_run: bool,
        amounts_per_run: List[int],
        n_fixed_inter: int,
        n_mixed_inter: int,
        n_flex_inter: int,
        currencies: List,
        agents_dict: dict,
        interactions_dict: dict,
        propose_decide_alignment: bool,
    ) -> "Context":
        """
        Creates a context (i.e. context for the MDP / Meta-Prompt run).
        """
        # buffer for storing conversation history
        buffer = ConversationBuffer()
        # meta prompt model
        meta_model = MetaPromptModel(llm=meta_llm, model_id="system")

        return Context(
            _id=_id, 
            name=name,
            task_prompt_dictator = task_prompt_dictator,
            task_prompt_decider = task_prompt_decider,
            meta_prompt=meta_prompt,
            verbose=verbose,
            test_run=test_run,
            buffer=buffer,
            meta_model=meta_model,
            amounts_per_run=amounts_per_run,
            n_fixed_inter=n_fixed_inter,
            n_mixed_inter=n_mixed_inter,
            n_flex_inter=n_flex_inter,
            currencies=currencies,
            agents_dict=agents_dict,
            interactions_dict=interactions_dict,
            user_llm=user_llm,
            assistant_llm=assistant_llm,
            meta_llm=meta_llm,
            propose_decide_alignment=propose_decide_alignment,
        )

    # This function loops through the users that the operator requested and creates a prompt for each of them, depending on whether they are flex of fixed
    def create_users(self,
                     agents_dict: dict, 
                     currencies: List[str], 
                     n_fixed: int, 
                     n_mixed: int, 
                     n_flex: int,
                     ) ->  Tuple[List[UserPrompt], List[AssistantPrompt]]:
        fixed_prompts = []
        utilities_dict = utilities_dict_for_all_2 if self.propose_decide_alignment else utilities_dict_for_all
        if n_fixed or n_mixed:
            for agent in agents_dict.fixed_agents:
                utilities = "You are in a simulator, and in this simulator, you must follow this principle:"
                # Get the utility regarding each currency
                for currency in currencies:
                    utilities += utilities_dict[agent.utilities[currency]].format(currency=currency)
                # Create the user_prompt
                fixed_prompts.append(UserPrompt(
                    id=agent.name,
                    utility=utilities,
                    utilies_dict=utilities_dict,
                    manners=agent.manners,
                    role="system",
                    content=content[0]
                ))
        flex_prompts = []
        if n_flex or n_mixed:
            # Create the assistant prompt
            for agent in agents_dict.flex_agents:
                flex_prompts.append(AssistantPrompt(
                    id=agent.name,
                    role="system",
                    manners=agent.manners,
                    content="""{task}"""
                ))
        return fixed_prompts, flex_prompts

    # This function pairs up the prompts according to how the operator specifid the pairings to be
    def create_pairs(self,
                     interactions: dict, 
                     fixed_prompts: List, 
                     flex_prompts: List, 
                     run_num: int, 
                     all_same: bool) -> List[Tuple]:
        fixed_prompt_names = [elem.id for elem in fixed_prompts]
        flex_prompt_names = [elem.id for elem in flex_prompts]
        result = []
        currencies_to_split = []
        run_num = f"run_1" if all_same else f"run_{run_num + 1}"
        
        for interaction in interactions.runs[run_num]:
            interaction = interaction.split('-')
            # If the dictator is a fixed agent, use the name associated with the corresponding fixed agent
            if "fixed" in interaction[0]:
                index_1 = (fixed_prompt_names.index(interaction[0]), True)
            # Otherwise, use the name associated with the corresponding flex agent
            else:
                index_1 = (flex_prompt_names.index(interaction[0]), False)
            # If the dictator is a fixed agent, use the name associated with the corresponding fixed agent
            if "fixed" in interaction[1]:
                index_2 = (fixed_prompt_names.index(interaction[1]), True)
            # Otherwise, use the name associated with the flex agent
            else:
                index_2 = (flex_prompt_names.index(interaction[1]), False)

            currencies_to_split.append(interaction[2])

            dictator_prompt = fixed_prompts[index_1[0]] if index_1[1] else flex_prompts[index_1[0]]
            decider_prompt = fixed_prompts[index_2[0]] if index_2[1] else flex_prompts[index_2[0]]
            result.append((dictator_prompt, decider_prompt))
        return result, currencies_to_split


    def get_amounts(
        self, 
        index: int,
        dictator_str: str, 
        decider_str: str,  
        dictator_scores: list,
        decider_scores: list,
        proposals: list,
    ) -> None:
        
        # Extract all numbers from the string
        numbers = [int(num) for num in re.findall(r'\d+', dictator_str['response'])]
        
        # Drop numbers at the indices 1, 4, 7, ... using list comprehension
        numbers = [num for idx, num in enumerate(numbers) if (idx + 1) % 3 != 1]

        # numbers = re.findall(r'will get (\d+)', dictator_str['response'].replace(',', '')) 
        # # Remove commas
        # numbers = [int(num.replace(',', '')) for num in numbers]

        accept = True if "accept" in decider_str['response'].lower() else False
        dict_scores = {}
        deci_scores = {}
        prop = {}
        for i in range(0, len(numbers), 2):
            if i // 2 > len(self.currencies) - 1:
                continue
            dict_scores[self.currencies[i // 2]] = numbers[i]
            deci_scores[self.currencies[i // 2]] = numbers[i + 1]
            prop[self.currencies[i // 2]] = numbers[i], numbers[i + 1]
        proposals.append(prop)
        if accept:
            dictator_scores[index] = dict_scores
            decider_scores[index] = deci_scores
        else:
            dictator_scores[index] = 0
            decider_scores[index] = 0


    # This function takes in a list of paired prompts and pairs them with the corresponding models
    # returns list with tuples structured as this: (prompt_dictator, model_dictator, prompt_decider, model_decider)
    def pair_models_with_prompts(
        self,
        user_llm: UserModel, 
        assistant_llm: AssistantAgent, 
        prompt_pairs: List[tuple],
    ) -> List:

        pairs = []
        id = 0
        for (prompt_dictator, prompt_decider) in prompt_pairs:
            pair = [prompt_dictator, prompt_decider]
            if type(prompt_dictator) == UserPrompt: # If the dictator is a user, use the user_llm
                model_dictator = UserModel(llm=user_llm, model_id=str(id))
            else: # Otherwise, use the assistant_llm
                model_dictator = AssistantAgent(llm=assistant_llm, model_id=str(id))
            pair.insert(1, model_dictator)
            if type(prompt_decider) == UserPrompt: # If the decider is a user, use the user_llm
                model_decider = UserModel(llm=user_llm, model_id=str(id))
            else: # Otherwise, use the assistant_llm
                model_decider = AssistantAgent(llm=assistant_llm, model_id=str(id))
            pair.insert(3, model_decider)
            pairs.append(pair)
            id += 1
        return pairs


    # This function runs one run of the experiment
    def run(
        self,
        run: int,
    ) -> None:
        # Creates a list of fixed UserPrompt templates and a list of flexible AssistantPrompt templates depending on the specifications of the operator
        fixed_prompts, flex_prompts = self.create_users(self.agents_dict, self.currencies, self.n_fixed_inter, self.n_mixed_inter, self.n_flex_inter)
        # Create a list of pairs of (dictator_prompt, decider_prompt)
        pairs, currencies_to_split = self.create_pairs(self.interactions_dict, fixed_prompts, flex_prompts, run, self.interactions_dict.all_same)
        # Extend every pair to include appropriate models and labels
        pairs = self.pair_models_with_prompts(self.user_llm, self.assistant_llm, pairs)

        # Gets the amount of currency that will be split 
        amount = self.amounts_per_run[run]

        user_proposals, user_scores_dictator, user_scores_decider = [], [-1] * len(pairs), [-1] * len(pairs)
        assistant_proposals, assistant_scores_dictator, assistant_scores_decider = [], [-1] * len(pairs), [-1] * len(pairs)

        for i, pair in enumerate(pairs):

            stipulation = ""
            currencies_lst = currencies_to_split[i].split(',')
            amount_and_currency = ""
            for j, currency in enumerate(currencies_lst):
                prefix = " and " if j >= 1 else ""
                amount_and_currency += f"{prefix}{amount} {currency}"
                stipulation += STIPULATIONS[currency]

            prompt_dictator, model_dictator, prompt_decider, model_decider = pair

            # calls either the fixed or flex agent as dictator

            dictator_response = model_dictator.run(buffer=self.buffer,
                                amount_and_currency=amount_and_currency,
                                stipulations=stipulation,
                                agent_prompt=prompt_dictator,
                                task_prompt=self.task_prompt_dictator,
                                is_dictator=True,
                                verbose=self.verbose)

            if type(prompt_dictator) == UserPrompt:
                prefix = "fixed" 
                user_dictator = True
            else:
                prefix = "flexible" 
                user_dictator = False

            self.buffer.save_agent_context(model_id=f"{model_dictator.model_id}_{prefix}_policy_dictator", **dictator_response)

            # calls either the fixed or flex agent as decider
            
            decider_response = model_decider.run(buffer=self.buffer,
                                    amount_and_currency = amount_and_currency,
                                    stipulations=stipulation,
                                    agent_prompt=prompt_decider,
                                    task_prompt=self.task_prompt_decider,
                                    is_dictator=False,
                                    verbose=self.verbose)
                                
            if type(prompt_decider) == UserPrompt:
                prefix = "fixed" 
                user_decider = True
            else:
                prefix = "flexible" 
                user_decider = False
                    
            self.buffer.save_agent_context(model_id=f"{model_decider.model_id}_{prefix}_policy_decider", **decider_response)

            if user_dictator and user_decider:
                dictator, decider, proposals = user_scores_dictator, user_scores_decider, user_proposals
            elif user_dictator and not user_decider:
                dictator, decider, proposals = user_scores_dictator, assistant_scores_decider, user_proposals
            elif not user_dictator and user_decider:
                dictator, decider, proposals = assistant_scores_dictator, user_scores_decider, assistant_proposals
            else:
                dictator, decider, proposals = assistant_scores_dictator, assistant_scores_decider, assistant_proposals

            self.get_amounts(i, dictator_response, decider_response, dictator, decider, proposals)
        # run meta-prompt at end of conversation
        meta_response = self.meta_model.run(
                                            buffer=self.buffer,
                                            meta_prompt=self.meta_prompt,
                                            run=run,
                                            n_fixed=self.n_fixed_inter,
                                            n_mixed=self.n_mixed_inter,
                                            verbose=self.verbose,
                                            )                 
        # save meta-prompt response for start of next conversation
        self.buffer.save_system_context(model_id="system", **meta_response)
        return user_scores_dictator, user_scores_decider, assistant_scores_dictator, assistant_scores_decider, user_proposals, assistant_proposals