from typing import List, Tuple


from scai.games.dictator_games.all_agents.user import UserModel
from scai.games.dictator_games.all_agents.assistant import AssistantAgent
from scai.games.dictator_games.all_agents.meta import MetaPromptModel


from scai.games.dictator_games.all_prompts.user.user_class import UserPrompt
from scai.games.dictator_games.all_prompts.user.user_prompt_template import utilities_dict_for_all, content

from scai.games.dictator_games.all_prompts.assistant.assistant_class import AssistantPrompt

from scai.games.dictator_games.all_prompts.task.task_prompt_template import STIPULATIONS


from scai.memory.buffer import ConversationBuffer
import re
import random

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
    ) -> None:
        """
        Initializes a context (i.e. context for the MDP / Meta-Prompt run).

        Args:
            _id (str): ID of the context.
            name (str): Name of the context.
            task_prompt (str): Task prompt.
            user_prompts (List[str]): User prompts.
            assistant_prompts (List[str]): Assistant prompts.
            meta_prompt (str): Meta prompt.
            metric_prompt (str): Metric prompt.
            buffer (ConversationBuffer): Conversation buffer.
            user_models (List[UserModel]): User models.
            assistant_models (List[AssistantAgent]): Assistant models.
            meta_model (MetaPromptModel): Meta-prompt model.
            verbose (bool): Whether to print the prompt.
            test_run (bool): Whether to run in test mode.
            max_tokens_user (int): Maximum number of tokens for the user.
            max_tokens_assistant (int): Maximum number of tokens for the assistant.
            max_tokens_meta (int): Maximum number of tokens for the meta-prompt.

        Returns:
            None
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
        self.n_fixed_inter = n_fixed_inter,
        self.n_mixed_inter = n_mixed_inter,
        self.n_flex_inter = n_flex_inter,
        # models and buffer
        self.buffer = buffer
        self.meta_model = meta_model
        self.user_llm = user_llm,
        self.assistant_llm = assistant_llm,
        self.meta_llm = meta_llm,



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
        n_fixed_inter : int,
        n_mixed_inter : int,
        n_flex_inter : int,
        currencies: List,
        agents_dict: dict,
        interactions_dict: dict,
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
            n_fixed_inter = n_fixed_inter,
            n_mixed_inter = n_mixed_inter,
            n_flex_inter = n_flex_inter,
            currencies=currencies,
            agents_dict=agents_dict,
            interactions_dict=interactions_dict,
            user_llm = user_llm,
            assistant_llm = assistant_llm,
            meta_llm = meta_llm,
        )

    # This function loops through the users that the operator requested and creates a prompt for each of them, depending on whether they are flex of fixed
    def create_users(self,
                     agents_dict: dict, 
                     currencies: List[str], 
                     n_fixed: int, 
                     n_mixed: int, 
                     n_flex: int) ->  Tuple[List[UserPrompt], List[AssistantPrompt]]:
        fixed_prompts = []
        if n_fixed or n_mixed:
            for agent in agents_dict.fixed_agents:
                utilities = "You are in a simulator, and in this simulator, you must follow this principle: Principle: "
                # Get the utility regarding each currency
                for currency in currencies:
                    utilities += utilities_dict_for_all[agent.utilities[currency]].format(currency=currency)
                # Create the user_prompt
                fixed_prompts.append(UserPrompt(
                    id=agent.name,
                    utility=utilities,
                    utilies_dict=utilities_dict_for_all,
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


    # def get_amounts(
    #     self, 
    #     index: int,
    #     dictator_str: str, 
    #     decider_str: str,  
    #     dictator_scores: list,
    #     decider_scores: list,
    #     proposals: list,
    #     user: bool,
    #     currency: str,
    #     assistant_dominant: bool
    # ) -> None:

    #     dictator_money = re.search(r'\d+', amount[1]).group()
    #     decider_money = re.search(r'\d+', amount[2]).group()
    #     dictator_money, decider_money = int(dictator_money), int(decider_money)
    #     if user or assistant_dominant:
    #         proposals.append((dictator_money, decider_money))
    #     accept = 1 if "accept" in decider_str['response'].lower() else 0
    #     if accept:
    #         if user:
    #             dictator_scores[index] = dictator_money
    #             decider_scores[index] = decider_money
    #         elif assistant_dominant:
    #             dictator_scores[index] = dictator_money
    #         else:
    #             decider_scores[index] = decider_money


    # takes in a list of paired prompts
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
            if type(prompt_dictator) == UserPrompt:
                model_dictator = UserModel(llm=user_llm, model_id=str(id))
            else:
                model_dictator = AssistantAgent(llm=assistant_llm, model_id=str(id))
            pair.insert(1, model_dictator)
            if type(prompt_decider) == UserPrompt:
                model_decider = UserModel(llm=user_llm, model_id=str(id))
            else:
                model_decider = AssistantAgent(llm=assistant_llm, model_id=str(id))
            pair.insert(3, model_decider)
            pairs.append(pair)
            id += 1
        return pairs


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

        user_proposals, user_scores_dictator, user_scores_decider = [], [0] * 1, [0] * 1
        assistant_proposals, assistant_scores_dictator, assistant_scores_decider = [], [0] * 4, [0] * 4
        
        for i, pair in enumerate(pairs):

            stipulation = ""
            currencies_lst = currencies_to_split[i].split(',')
            amount_and_currency = ""
            for i, currency in enumerate(currencies_lst):
                prefix = " and " if i > 1 else ""
                amount_and_currency += f"{prefix} {amount} {currency}"
                stipulation += STIPULATIONS[currency]

            prompt_dictator, model_dictator, prompt_decider, model_decider = pair

            dictator_response = model_dictator.run(buffer=self.buffer,
                                amount_and_currency=amount_and_currency,
                                stipulations=stipulation,
                                agent_prompt=prompt_dictator,
                                task_prompt=self.task_prompt_dictator,
                                is_dictator=True,
                                verbose=self.verbose)
                                
            self.buffer.save_user_context(model_id=f"{model_dictator.model_id}_dictator", **dictator_response)
            
            decider_response = model_decider.run(buffer=self.buffer,
                                    amount_and_currency = amount_and_currency,
                                    stipulations=stipulation,
                                    agent_prompt=prompt_decider,
                                    task_prompt=self.task_prompt_decider,
                                    is_dictator=False,
                                    verbose=self.verbose)
                                    
            self.buffer.save_user_context(model_id=f"{model_decider.model_id}_decider", **decider_response)
                
        # run meta-prompt at end of conversation
        meta_response = self.meta_model.run(buffer=self.buffer,
                                            meta_prompt=self.meta_prompt,
                                            task_prompt=self.task_prompt_dictator, 
                                            run=run,
                                            verbose=self.verbose)                 
        # save meta-prompt response for start of next conversation
        self.buffer.save_system_context(model_id="system", **meta_response)
        return user_scores_dictator, user_scores_decider, assistant_scores_dictator, assistant_scores_decider, user_proposals, assistant_proposals