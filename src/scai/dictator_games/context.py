from typing import List, Tuple


from scai.dictator_games.agents.user import UserModel
from scai.dictator_games.agents.assistant import AssistantAgent
from scai.dictator_games.agents.meta import MetaPromptModel
from scai.dictator_games.agents.oracle import OracleAgent


from scai.dictator_games.prompts.user.user_class import UserPrompt
from scai.dictator_games.prompts.user.user_prompt import utilities_dict_for_all, utilities_dict_fixed_decider_behavior, utilities_empty, content, content_with_manners

from scai.dictator_games.prompts.assistant.assistant_class import AssistantPrompt

from scai.dictator_games.prompts.oracle.oracle_class import OraclePrompt

from scai.memory.buffer import ConversationBuffer

import re

import time

class Context():
    def __init__(
        self, 
        _id: List[str],
        name: str, 
        task_prompt_dictator: str, 
        task_prompt_decider: str,
        meta_prompt: str, 
        buffer: List[ConversationBuffer], 
        meta_model: MetaPromptModel, 
        verbose: bool, 
        test_run: bool,
        currencies: List[List[str]],
        amounts_per_run: List[List[int]],
        agents_dict: List[dict],
        interactions_dict: dict,
        edge_case_instructions: str,
        include_reason: bool,
        user_llm: UserModel,
        assistant_llm: AssistantAgent,
        meta_llm: MetaPromptModel,
        oracle_llm: OracleAgent,
        propose_decide_alignment: bool,
        has_manners: bool,
        ask_question: bool,
        ask_question_train: bool,
        set_fixed_agents: bool,
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
        assert len(_id) == len(currencies) == len(amounts_per_run) == len(agents_dict) == len(buffer)
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
        self.propose_decide_alignment = propose_decide_alignment
        self.content = content if has_manners else content_with_manners
        self.ask_question = ask_question
        self.ask_question_train = ask_question_train
        # agents and interactions dictionaries
        self.currencies = currencies
        self.agents_dict = agents_dict
        self.interactions_dict = interactions_dict
        self.set_fixed_agents = set_fixed_agents
        # run settings
        self.test_run = test_run
        self.amounts_per_run = amounts_per_run
        # models and buffer
        self.buffer = buffer
        self.meta_model = meta_model
        self.user_llm = user_llm
        self.assistant_llm = assistant_llm
        self.meta_llm = meta_llm
        self.oracle_llm = oracle_llm
        
        self.total_experiments = len(self.currencies)

 
    @staticmethod
    def create(
        user_llm: UserModel, 
        assistant_llm: AssistantAgent, 
        meta_llm: MetaPromptModel, 
        oracle_llm: OracleAgent,
        _id: List[str], 
        name: str, 
        task_prompt_dictator: str, 
        task_prompt_decider: str,
        meta_prompt: str,
        verbose: bool,
        test_run: bool,
        amounts_per_run: List[int],
        currencies: List[List[str]],
        agents_dict: List[dict],
        interactions_dict: dict,
        include_reason: bool,
        edge_case_instructions: str,
        propose_decide_alignment: bool,
        has_manners: bool,
        ask_question: bool,
        ask_question_train: bool,
        set_fixed_agents: bool
    ) -> "Context":
        """
        Creates a context (i.e. context for the MDP / Meta-Prompt run).
        """
        # buffer for storing conversation history
        buffer = [ConversationBuffer() for _ in range(len(_id))]
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
            currencies=currencies,
            agents_dict=agents_dict,
            interactions_dict=interactions_dict,
            edge_case_instructions=edge_case_instructions,
            include_reason=include_reason,
            user_llm=user_llm,
            assistant_llm=assistant_llm,
            meta_llm=meta_llm,
            oracle_llm=oracle_llm,
            propose_decide_alignment=propose_decide_alignment,
            has_manners=has_manners,
            ask_question=ask_question,
            ask_question_train=ask_question_train,
            set_fixed_agents=set_fixed_agents 
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
            # If you're creating fixed-policy agents, then use UserPrompts and add utilites
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
            # Otherwise, you're creating flexible-policy agents, use AssistantPrompts and add relevant information
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
                     ) ->  Tuple[List[UserPrompt], List[AssistantPrompt]]:
        # Set the utilities according to the "psychopath "
        utilities_dict = utilities_dict_fixed_decider_behavior if self.propose_decide_alignment else utilities_dict_for_all
        # Generate the prompts for the fixed agents
        fixed_agent_prompts = self.generate_agent_prompts(agents_dict.fixed_agents, currencies, utilities_dict, "fixed")
        # Generate the prompts for the flexible agents
        flex_agent_prompts = self.generate_agent_prompts(agents_dict.flex_agents, currencies, utilities_dict, "flex")
        return fixed_agent_prompts, flex_agent_prompts

    # This function pairs up the prompts according to how the operator specifid the pairings to be
    def pair_prompts(self,
                     interactions: dict, 
                     fixed_prompts: List, 
                     flex_prompts: List, 
                     ) -> List[Tuple]:
        # Gather all of the fixed-policy agents
        fixed_prompt_ids = [elem.id for elem in fixed_prompts]
        # Gather all of the flexible-policy agents
        flex_prompt_ids = [elem.id for elem in flex_prompts]
        # Pairs carries the pairs of agents that interact in each iteration, currencies contains what currencies they're splitting
        pairs = []
        # If the runs are all the same, just use the first run, otherwise use the specified run number
        
        # For every interaction, pair off the agents according to the interaction specifications
        for interaction in interactions.runs[f"run_1"]:
            interaction = interaction.split('-')
            first_agent, second_agent = interaction[0], interaction[1]
            # use the prompt associated with the correct agent depending on whether the dictator is a dictator or decider
            if "fixed" in first_agent:
                dictator_prompt = fixed_prompts[fixed_prompt_ids.index(first_agent)]
            else:
                dictator_prompt = flex_prompts[flex_prompt_ids.index(first_agent)]

            # If the decider is a fixed agent, use the name associated with the corresponding fixed agent
            if "fixed" in second_agent:
                decider_prompt = fixed_prompts[fixed_prompt_ids.index(second_agent)]
            else:
                decider_prompt = flex_prompts[flex_prompt_ids.index(second_agent)]

            # "Pairs up" the prompts, meaning they will interact later.
            pairs.append((dictator_prompt, decider_prompt))

        return pairs


    def get_amounts(
        self, 
        index: int,
        dictator_str: str, 
        decider_str: str,  
        dictator_scores: list,
        decider_scores: list,
        proposals: list,
        experiment_num: int,
    ) -> None:
        #if the dictator string contains a substring that starts with "I choose option 2." or "I choose option 1.", then remove that substring
        if dictator_str['response'].find("I choose option 2.") != -1:
            dictator_str['response'] = dictator_str['response'].replace("I choose option 2.", "")
        elif dictator_str['response'].find("I choose option 1.") != -1:
            dictator_str['response'] = dictator_str['response'].replace("I choose option 1.", "")

        # Extract all numbers from the string
        numbers = [int(num) for num in re.findall(r'\d+', dictator_str['response'])]
        
        # Drop numbers at the indices 1, 4, 7, ... using list comprehension
        numbers = [num for idx, num in enumerate(numbers) if (idx + 1) % 3 != 1]

        # indicates whether the proposal was accepted or not
        accept = True if "accept" in decider_str['response'].lower() else False

        currencies = self.currencies[experiment_num]

        # For one interaction, dict_scores contains the amounts the dictator gets, deci_scores contains the amount the decider gets, and prop contains the proposals
        dict_scores, deci_scores, prop = {}, {}, {}
        # This loop amounts for the potential of splitting more than one currency split, where the dictator must propose separate splits for every currency included
        for i in range(0, len(numbers), 2):
            # If the agent happened to include extra numbers other than the proposal, don't consider these numbers
            if i // 2 > len(self.currencies) - 1:
                continue
            # The amount the dictator proposed to itself is the first number, and the amount that the dictator proposed to the decider is the second number
            dictator_gets = numbers[i]
            decider_gets = numbers[i+1] if len(numbers) > i+1 else 1
            # If the proposal is accepted then add the respective amounts gained
            if accept:
                dict_scores[currencies[0]], deci_scores[currencies[0]] = dictator_gets, decider_gets
            # Include both amounts in the entire proposal
            prop[currencies[0]] = dictator_gets, decider_gets
        proposals.append(prop)
        # If the proposal is accepted, add the scores, as the values they are
        if accept:
            dictator_scores[index], decider_scores[index] = dict_scores, deci_scores
        # Otherwise, indicate that both parties recieved nothing with 0's
        else:
            dictator_scores[index], decider_scores[index] = 0, 0


    # This function takes in a list of paired prompts and pairs them with the corresponding models
    # returns list with tuples structured as this: (prompt_dictator, model_dictator, prompt_decider, model_decider)
    def return_models(
        self,
        user_llm: UserModel, 
        assistant_llm: AssistantAgent, 
        prompt_pairs: List[tuple],
    ) -> List:
        pairs = []
        id = 0
        for (prompt_dictator, prompt_decider) in prompt_pairs:
            # initialize the pairs with empty space for the models next to the prompts
            pair = [None, None]

            # If the dictator is a fixed-policy agent, use the user_llm
            if type(prompt_dictator) == UserPrompt:
                model_dictator = UserModel(llm=user_llm, model_id=str(id))
             # Otherwise, the dictator is a flexible-policy agent, use the assistant_llm
            else:
                model_dictator = AssistantAgent(llm=assistant_llm, model_id=str(id))
            # Insert the model next to the dictator prompt
            pair[0] = model_dictator
            # If the decider is a fixed-policy agent, use the user_llm
            if type(prompt_decider) == UserPrompt:
                model_decider = UserModel(llm=user_llm, model_id=str(id))
            # Otherwise, the decider is a flexible-policy agent, use the assistant_llm
            else:
                model_decider = AssistantAgent(llm=assistant_llm, model_id=str(id))
            # Insert the model next to the decider prompt
            pair[1] = model_decider
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
        all_prompts = {}
        for i, (agent_dict, currencies) in enumerate(zip(self.agents_dict, self.currencies)):
            fixed_prompts, flex_prompts = self.create_user_prompts(agent_dict, currencies)
            all_prompts[i] = fixed_prompts, flex_prompts
        # Create a list of pairs of (dictator_prompt, decider_prompt)
        all_interactions = {}
        for i in range(self.total_experiments):
            fixed_prompts, flex_prompts = all_prompts[i]
            pairs = self.pair_prompts(self.interactions_dict, fixed_prompts, flex_prompts)
            all_interactions[i] = pairs

        # Extend every pair to include appropriate models and labels
        pairs = self.return_models(self.user_llm, self.assistant_llm, all_interactions[0])

        # Keeps track of the proposals the fixed-policy agent made, the income it recieved as a dictator, and the income it received as a decider
        # Keeps track of the proposals the flexible-policy agent made, the income it recieved as a dictator, and the income it received as a decider
        # Both score lists are initialized with -1's to indicate that no interaction occured at that time point for that specific type of agent in that specific role
        # If an interaction didn't happen, this -1 will remain, otherwise it will be replaced with a number depending on the proposal/whether it was accepted or rejected
        all_proposals = [[] for _ in range(self.total_experiments)]
        for i in range(self.total_experiments):
            user_proposals, user_scores_dictator, user_scores_decider = [], [-1] * len(pairs), [-1] * len(self.interactions_dict.runs[f"run_1"])
            assistant_proposals, assistant_scores_dictator, assistant_scores_decider = [], [-1] * len(pairs), [-1] * len(self.interactions_dict.runs[f"run_1"])
            all_proposals[i] = user_scores_dictator, user_scores_decider, assistant_scores_dictator, assistant_scores_decider, user_proposals, assistant_proposals

        num_questions_asked = [0] * self.total_experiments
        num_total_flex_dictators = 0
        ###########################
        # For every agent pair in pairs, simulate an interaction between those two agents
        for i in range(len(self.interactions_dict.runs[f"run_1"])):
            # Keep track of what needs to be split and what amount of it needs to be split, as well as any special instructions for splitting that resource (stipulations)

            model_dictator, model_decider = pairs[i][0], pairs[i][1]
            # For each currency, add specific instructions pertaining to that currency using stipulations. In addition, keep track of what and how much you're splitting
            amounts_and_currencies = {}
            stipulations = {}
            for k in range(self.total_experiments):
                amount_and_currency = ""
                stipulation = ""
                for j, currency in enumerate(self.currencies[k]):
                    prefix = " and " if j >= 1 else ""
                    amount_and_currency += f"{prefix}{self.amounts_per_run[k][run]} {currency}"
                    stipulation += "When splitting the resource, please only propose integer values greater than or equal to zero. "
                amounts_and_currencies[k] = amount_and_currency
                stipulations[k] = stipulation

            # Each pair contains the dictator's prompt, followed by the model, then the decider's prompt, followed by the decider's model
            dictator_prompts = {}
            decider_prompts = {}
            for k in range(self.total_experiments):
                all_agents_paired_with_models = all_interactions[k]
                dictator_prompts[k] = all_agents_paired_with_models[i][0]
                decider_prompts[k] = all_agents_paired_with_models[i][1]
            # calls either the fixed or flex agent as dictator
            dictator_responses = model_dictator.run(buffer=self.buffer, # list
                                amount_and_currency=amounts_and_currencies, # dictionary
                                stipulations=stipulations, # dictionary
                                agent_prompt=dictator_prompts, # dictionary
                                task_prompt=self.task_prompt_dictator,
                                total_experiments=self.total_experiments,
                                edge_case_instructions=self.edge_case_instructions,
                                include_reason=self.include_reason,
                                ask_question=self.ask_question,
                                ask_question_train=self.ask_question_train,
                                set_fixed_agents=self.set_fixed_agents,
                                asked_oracle=False,
                                oracle_response="",
                                is_dictator=True,
                                run_num=run,
                                verbose=self.verbose)
            
            time.sleep(10)

            # If the fixed agent was the dictator, save the response as a fixed agent's response, and indicate that the dictator was fixed
            if type(model_dictator) == UserModel:
                prefix_dic, user_dictator = "fixed", True 
            # Otherwise, the flexible agent was the dictator, save the reponse as a flexible agent's response, and indicate that the dictator was flex
            else:
                prefix_dic, user_dictator = "flexible", False
                num_total_flex_dictators += 1

            for j, buf in enumerate(self.buffer):
                buf.save_agent_context(model_id=f"{model_dictator.model_id}_{prefix_dic}_policy_dictator", **dictator_responses[j])
            # if dictator_response['response'].find("Question?") != -1:
            #     num_questions_asked += 1
            #     # Prompt the oracle
            #     oracle_agent = OracleAgent(llm=self.oracle_llm, model_id="0")
            #     num_iterations = 0
            #     while dictator_response['response'].find("Question?") != -1:
            #         oracle_response = oracle_agent.run(agent_prompt=OraclePrompt, verbose=self.verbose)
            #         oracle_response = {'response': "Your current principle applies in this scenario, even under different currencies and amounts. Please follow your previously learned principle TO THE EXTREME! If you're sitll unsure of how to make the split, ask another question. If you do so, please indicate it like so: Question?:... Otherwise, please structure your proposal exactly the same as this: (Be sure to include ALL three numbers in integer forms): For the Z amount of \{given_currency\}, The proposer will get X, and the decider will get Y."}
            #         self.buffer.save_agent_context(model_id=f"{model_dictator.model_id}_oracle_response_to_agent_{num_iterations}", **oracle_response)

            #         num_iterations += 1
            #         # Prompt the agent again
            #         dictator_response = model_dictator.run(buffer=self.buffer,
            #                         amount_and_currency=amount_and_currency,
            #                         stipulations=stipulation,
            #                         agent_prompt=dictator_prompts,
            #                         task_prompt=self.task_prompt_dictator,
            #                         total_experiments=self.total_experiments,
            #                         edge_case_instructions=self.edge_case_instructions,
            #                         include_reason=self.include_reason,
            #                         ask_question=self.ask_question,
            #                         ask_question_train=self.ask_question_train,
            #                         set_fixed_agents=self.set_fixed_agents,
            #                         asked_oracle=True,
            #                         oracle_response=oracle_response['response']+f"{num_iterations}",
            #                         is_dictator=True,
            #                         run_num=run,
            #                         verbose=self.verbose)

            #         if self.verbose:
            #             print('===================================')
            #             print("Flex-agent's response:")
            #             print(dictator_response['response'] + "\n")

            #         self.buffer.save_agent_context(model_id=f"{model_dictator.model_id}_{prefix}_agent_response_to_oracle_{num_iterations}", **dictator_response)

            # calls either the fixed or flex agent as decider
            decider_responses = model_decider.run(buffer=self.buffer,
                                    amount_and_currency=amounts_and_currencies,
                                    stipulations=stipulations,
                                    agent_prompt=decider_prompts,
                                    task_prompt=self.task_prompt_decider,
                                    total_experiments=self.total_experiments,
                                    edge_case_instructions=self.edge_case_instructions,
                                    include_reason=self.include_reason,
                                    ask_question=self.ask_question,
                                    ask_question_train=self.ask_question_train,
                                    set_fixed_agents=self.set_fixed_agents,
                                    asked_oracle=False,
                                    oracle_response="",
                                    is_dictator=False,
                                    run_num=run,
                                    verbose=self.verbose)
            
            time.sleep(10)
                                
            # If the fixed agent was the dedcider, save the response as a fixed agent's response, and indicate that the dictator was fixed
            if type(model_decider) == UserPrompt:
                prefix_deci, user_decider = "fixed", True
            # Otherwise, the flexible agent was the decider, save the reponse as a flexible agent's response, and indicate that the dictator was flex
            else:
                prefix_deci, user_decider = "flexible", False
            
            for j, buf in enumerate(self.buffer):
                buf.save_agent_context(model_id=f"{model_decider.model_id}_{prefix_deci}_policy_decider", **decider_responses[j])
            
            # If the fixed agent was the dictator and the decider, set the output scores list to be the one associated with fixed agents
            for j in range(self.total_experiments):
                user_scores_dictator, user_scores_decider, assistant_scores_dictator, assistant_scores_decider, user_proposals, assistant_proposals = all_proposals[j]

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
                self.get_amounts(i, dictator_responses[j], decider_responses[j], dictator, decider, proposals, j)
        # run meta-prompt at end of conversation
        meta_response = self.meta_model.run(
                                            buffer=self.buffer,
                                            meta_prompt=self.meta_prompt,
                                            run=run,
                                            dictator=prefix_dic,
                                            decider=prefix_deci,
                                            verbose=self.verbose,
                                            )                 
        # save meta-prompt response for start of next conversation
        for j, buf in enumerate(self.buffer):
            buf.save_system_context(model_id="system", **meta_response[j])

        time.sleep(self.total_experiments*10)

        return all_proposals, [question / num_total_flex_dictators for question in num_questions_asked]