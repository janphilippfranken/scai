from typing import List, Tuple


from scai.games.ultimatum_games.agents.user import UserModel
from scai.games.ultimatum_games.agents.assistant import AssistantAgent
from scai.games.ultimatum_games.agents.meta import MetaPromptModel


from scai.games.ultimatum_games.prompts.user.user_class import UserPrompt
from scai.games.ultimatum_games.prompts.user.user_prompt import utilities_dict_for_all, utilities_dict_fixed_decider_behavior, utilities_empty, content, content_with_manners

from scai.games.ultimatum_games.prompts.assistant.assistant_class import AssistantPrompt

from scai.games.ultimatum_games.prompts.task.task_prompt import STIPULATIONS


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
        edge_case_instructions: str,
        include_reason: bool,
        user_llm: UserModel,
        assistant_llm: AssistantAgent,
        meta_llm: MetaPromptModel,
        propose_decide_alignment: bool,
        has_manners: bool,
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
        self.edge_case_instructions = edge_case_instructions
        self.include_reason = include_reason
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
        self.content = content if has_manners else content_with_manners


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
        include_reason: bool,
        edge_case_instructions: str,
        propose_decide_alignment: bool,
        has_manners: bool,
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
            edge_case_instructions=edge_case_instructions,
            include_reason=include_reason,
            user_llm=user_llm,
            assistant_llm=assistant_llm,
            meta_llm=meta_llm,
            propose_decide_alignment=propose_decide_alignment,
            has_manners = has_manners,
        )
    # This function instantiates all of either the fixed-agent or flexible-agent prompts, to be paired off later
    def generate_agent_prompts(self,
                        all_agents: list,
                        currencies: list,
                        utilities_dict: dict,
                        prompt_type: str # either a user or assistant prompt
                        ) -> list:
        agents_list = []
        for agent in all_agents:
            # If you're pairing off fixed-policy agents, then use UserPrompts and add utilites
            if prompt_type == "fixed":
                currency_utilities = "You are in a simulator, and in this simulator, you must follow this principle:"
                for currency in currencies:
                    currency_utilities += utilities_dict[agent.utilities[currency]].format(currency=currency)
                new_agent = UserPrompt(
                    id=agent.name,
                    utility=currency_utilities,
                    utilities_dict=utilities_dict,
                    manners=agent.manners,
                    role="system",
                    content=self.content[0]
                )
            # Otherwise, you're pairing off flexible-policy agents, use AssistantPrompts and add relevant information
            elif prompt_type == "flex":
                new_agent = AssistantPrompt(
                    id=agent.name,
                    role="system",
                    manners=agent.manners,
                    content="""{task}""",
                    initial_principle = utilities_empty[agent.initial_util]
                )
            agents_list.append(new_agent)
        return agents_list

    # This function loops through the users that the operator requested and creates a prompt for each of them, depending on whether they are flex of fixed
    def create_user_prompts(self,
                     agents_dict: dict, 
                     currencies: List[str], 
                     n_fixed: int, 
                     n_mixed: int, 
                     n_flex: int,
                     ) ->  Tuple[List[UserPrompt], List[AssistantPrompt]]:
        # Instantiate these as empty in case there are no flexible or fixed agents needed
        fixed_agent_prompts, flex_agent_prompts = [], []
        utilities_dict = utilities_dict_fixed_decider_behavior if self.propose_decide_alignment else utilities_dict_for_all
        # If you need fixed agents, generate a list of the prompts
        if n_fixed or n_mixed:
            fixed_agent_prompts = self.generate_agent_prompts(agents_dict.fixed_agents, currencies, utilities_dict, "fixed")
        # If you need flexible agents, generate a list of the prompts
        if n_flex or n_mixed:
            flex_agent_prompts = self.generate_agent_prompts(agents_dict.flex_agents, currencies, utilities_dict, "flex")
        return fixed_agent_prompts, flex_agent_prompts

    # This function pairs up the prompts according to how the operator specifid the pairings to be
    def pair_prompts(self,
                     interactions: dict, 
                     fixed_prompts: List, 
                     flex_prompts: List, 
                     run_num: int, 
                     all_same: bool) -> List[Tuple]:
        # Gather all of the fixed-policy agents
        fixed_prompt_names = [elem.id for elem in fixed_prompts]
        # Gather all of the flexible-policy agents
        flex_prompt_names = [elem.id for elem in flex_prompts]
        # Result carries the pairs of agents that interact in each iteration, currencies contains what currencies they're splitting
        result, currencies_to_split = [], []
        # If the runs are all the same, just use the first run, otherwise use the specified run number
        run_num = f"run_1" if all_same else f"run_{run_num + 1}"
        
        # For every interaction, pair off the agents according to the interaction specifications
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
            # Append the currencies to split to the currencies
            currencies_to_split.append(interaction[2])

            dictator_prompt = fixed_prompts[index_1[0]] if index_1[1] else flex_prompts[index_1[0]]
            decider_prompt = fixed_prompts[index_2[0]] if index_2[1] else flex_prompts[index_2[0]]
            # Append the interaction to result
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

        # indicates whether the proposal was accepted or not
        accept = True if "accept" in decider_str['response'].lower() else False

        # For one interaction, dict_scores contains the amounts the dictator gets, deci_scores contains the amount the decider gets, and prop contains the proposals
        dict_scores, deci_scores, prop = {}, {}, {}
        # This loop amounts for the potential of splitting more than one currency split, where the dictator must propose separate splits for every currency included
        for i in range(0, len(numbers), 2):
            # If the agent happened to include extra numbers other than the proposal, don't consider these numbers
            if i // 2 > len(self.currencies) - 1:
                continue
            # The amount the dictator proposed to itself is the first number, and the amount that the dictator proposed to the decider is the second number
            dictator_gets = numbers[i]
            decider_gets = numbers[i + 1]
            # If the proposal is accepted then add the respective amounts gained
            if accept:
                dict_scores[self.currencies[i // 2]], deci_scores[self.currencies[i // 2]] = dictator_gets, decider_gets
            # Include both amounts in the entire proposal
            prop[self.currencies[i // 2]] = dictator_gets, decider_gets
        proposals.append(prop)
        # If the proposal is accepted, add the scores, as the values they are
        if accept:
            dictator_scores[index], decider_scores[index] = dict_scores, deci_scores
        # Otherwise, indicate that both parties recieved nothing with 0's
        else:
            dictator_scores[index], decider_scores[index] = 0, 0


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
            # initialize the pairs with empty space for the models next to the prompts
            pair = [prompt_dictator, None, prompt_decider, None]

            # If the dictator is a fixed-policy agent, use the user_llm
            if type(prompt_dictator) == UserPrompt:
                model_dictator = UserModel(llm=user_llm, model_id=str(id))
             # Otherwise, the dictator is a flexible-policy agent, use the assistant_llm
            else:
                model_dictator = AssistantAgent(llm=assistant_llm, model_id=str(id))
            # Insert the model next to the dictator prompt
            pair[1] = model_dictator
            # If the decider is a fixed-policy agent, use the user_llm
            if type(prompt_decider) == UserPrompt:
                model_decider = UserModel(llm=user_llm, model_id=str(id))
            # Otherwise, the decider is a flexible-policy agent, use the assistant_llm
            else:
                model_decider = AssistantAgent(llm=assistant_llm, model_id=str(id))
            # Insert the model next to the decider prompt
            pair[3] = model_decider
            # Append this interaction pair to the list of all pairs for interactions
            pairs.append(pair)
            id += 1
        return pairs


    # This function runs one run of the experiment
    def run(
        self,
        run: int,
    ) -> None:
        # Creates a list of fixed UserPrompt templates and a list of flexible AssistantPrompt templates depending on the specifications of the operator
        fixed_prompts, flex_prompts = self.create_user_prompts(self.agents_dict, self.currencies, self.n_fixed_inter, self.n_mixed_inter, self.n_flex_inter)
        # Create a list of pairs of (dictator_prompt, decider_prompt)
        pairs, currencies_to_split = self.pair_prompts(self.interactions_dict, fixed_prompts, flex_prompts, run, self.interactions_dict.all_same)
        # Extend every pair to include appropriate models and labels
        pairs = self.pair_models_with_prompts(self.user_llm, self.assistant_llm, pairs)

        # Gets the amount of currency that will be split 
        amount = self.amounts_per_run[run]

        # Keeps track of the proposals the fixed-policy agent made, the income it recieved as a dictator, and the income it received as a decider
        user_proposals, user_scores_dictator, user_scores_decider = [], [-1] * len(pairs), [-1] * len(pairs)
        # Keeps track of the proposals the flexible-policy agent made, the income it recieved as a dictator, and the income it received as a decider
        assistant_proposals, assistant_scores_dictator, assistant_scores_decider = [], [-1] * len(pairs), [-1] * len(pairs)
        # Both score lists are initialized with -1's to indicate that no interaction occured at that time point for that specific type of agent in that specific role
        # If an interaction didn't happen, this -1 will remain, otherwise it will be replaced with a number depending on the proposal/whether it was accepted or rejected

        # For every agent pair in pairs, simulate an interaction between those two agents
        for i, agent_pairing in enumerate(pairs):
            # Keep track of what needs to be split and what amount of it needs to be split, as well as any special instructions for splitting that resource (stipulations)
            currencies_lst = currencies_to_split[i].split(',')
            amount_and_currency = ""
            stipulation = ""

            # For each currency, add specific instructions pertaining to that currency using stipulations. In addition, keep track of what and how much you're splitting
            for j, currency in enumerate(currencies_lst):
                prefix = " and " if j >= 1 else ""
                amount_and_currency += f"{prefix}{amount} {currency}"
                if currency in STIPULATIONS:
                    stipulation += STIPULATIONS[currency]
                else:
                    stipulation += "When splitting the resource, please only propose integer values greater than or equal to zero. "

            # Each pair contains the dictator's prompt, followed by the model, then the decider's prompt, followed by the decider's model
            prompt_dictator, model_dictator, prompt_decider, model_decider = agent_pairing
            # calls either the fixed or flex agent as dictator
            dictator_response = model_dictator.run(buffer=self.buffer,
                                amount_and_currency=amount_and_currency,
                                stipulations=stipulation,
                                agent_prompt=prompt_dictator,
                                task_prompt=self.task_prompt_dictator,
                                edge_case_instructions=self.edge_case_instructions,
                                include_reason=self.include_reason,
                                is_dictator=True,
                                run_num=run,
                                verbose=self.verbose)

            # If the fixed agent was the dictator, save the response as a fixed agent's response, and indicate that the dictator was fixed
            if type(prompt_dictator) == UserPrompt:
                prefix, user_dictator = "fixed", True 
            # Otherwise, the flexible agent was the dictator, save the reponse as a flexible agent's response, and indicate that the dictator was flex
            else:
                prefix, user_dictator = "flexible", False
            self.buffer.save_agent_context(model_id=f"{model_dictator.model_id}_{prefix}_policy_dictator", **dictator_response)

            # calls either the fixed or flex agent as decider
            decider_response = model_decider.run(buffer=self.buffer,
                                    amount_and_currency = amount_and_currency,
                                    stipulations=stipulation,
                                    agent_prompt=prompt_decider,
                                    task_prompt=self.task_prompt_decider,
                                    edge_case_instructions=self.edge_case_instructions,
                                    include_reason=self.include_reason,
                                    is_dictator=False,
                                    run_num=run,
                                    verbose=self.verbose)
            # If the fixed agent was the dedcider, save the response as a fixed agent's response, and indicate that the dictator was fixed
            if type(prompt_decider) == UserPrompt:
                prefix, user_decider = "fixed", True
            # Otherwise, the flexible agent was the decider, save the reponse as a flexible agent's response, and indicate that the dictator was flex
            else:
                prefix, user_decider = "flexible", False
            self.buffer.save_agent_context(model_id=f"{model_decider.model_id}_{prefix}_policy_decider", **decider_response)
            
            # If the fixed agent was the dictator and the decider, set the output scores list to be the one associated with fixed agents
            if user_dictator and user_decider:
                dictator, decider, proposals = user_scores_dictator, user_scores_decider, user_proposals
            # Otherwise, the fixed agent was the dictator and the flex agent was the decider, set the dictator scores to be the fixed list, and the decider to be the flex one
            elif user_dictator and not user_decider:
                dictator, decider, proposals = user_scores_dictator, assistant_scores_decider, user_proposals
            # Otherwise, the flex and the fixed agent was the dictator, set the dictator scores to be the flex list, and the decider to be the fixed one
            elif not user_dictator and user_decider:
                dictator, decider, proposals = assistant_scores_dictator, user_scores_decider, assistant_proposals
            # Otherwise, the flex agent was the dictator and the decider, set the output scores list to be the one associated with flex agents
            else:
                dictator, decider, proposals = assistant_scores_dictator, assistant_scores_decider, assistant_proposals
            # Get the dictator income, decider income, and proposals after setting the correct type for the dictator and decider
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