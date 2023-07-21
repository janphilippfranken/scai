from typing import List


from scai.games.game_2.agents.user import UserModel
from scai.games.game_2.agents.assistant import AssistantAgent
from scai.games.game_2.agents.meta import MetaPromptModel

from scai.memory.buffer import ConversationBuffer

import random
from itertools import combinations

class Context():
    def __init__(
        self, 
        _id: str,
        name: str, 
        task_prompt_dictator: str, 
        task_prompt_decider: str,
        user_prompts: List[str], 
        assistant_prompts: List[str], 
        meta_prompt: str, 
        buffer: ConversationBuffer, 
        user_models_a: List[UserModel],
        user_models_b: List[UserModel],
        user_models_c: List[UserModel],
        assistant_models: List[AssistantAgent], 
        meta_model: MetaPromptModel, 
        verbose: bool, 
        test_run: bool,
        utility: str,
        n_user_interactions : int,
        n_assistant_interactions: int
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
        self.user_prompts = user_prompts
        self.assistant_prompts = assistant_prompts
        self.meta_prompt = meta_prompt
        self.verbose = verbose
        # run settings
        self.test_run = test_run
        # models and buffer
        self.buffer = buffer
        self.assistant_models = assistant_models
        self.meta_model = meta_model
        self.utility = utility
        self.n_user_interactions = n_user_interactions
        self.n_assistant_interactions = n_assistant_interactions
        self.user_models_a = user_models_a
        self.user_models_b = user_models_b
        self.user_models_c = user_models_c



    @staticmethod
    def create(
        user_llm: UserModel, 
        assistant_llm: AssistantAgent, 
        meta_llm: MetaPromptModel, 
        _id: str, 
        name: str, 
        task_prompt_dictator: str, 
        task_prompt_decider: str,
        user_prompts: List[str], 
        assistant_prompts: List[str], 
        meta_prompt: str,
        verbose: bool,
        test_run: bool,
        utility: str,
        n_user_interactions : int,
        n_assistant_interactions: int,
    ) -> "Context":
        """
        Creates a context (i.e. context for the MDP / Meta-Prompt run).
        """
        # buffer for storing conversation history
        buffer = ConversationBuffer()
        # user models

        user_models_a = [
            UserModel(llm=user_llm, model_id=str(model_id)) for model_id in range(n_user_interactions)
            ]
        user_models_b = [
            UserModel(llm=user_llm, model_id=str(model_id)) for model_id in range(n_user_interactions)
            ]
        user_models_c = [
            UserModel(llm=user_llm, model_id=str(model_id)) for model_id in range(n_assistant_interactions)
            ]
        # assistant models 
        assistant_models = [
            AssistantAgent(llm=assistant_llm, model_id=str(model_id)) for model_id in range(n_assistant_interactions)
            ]
        # meta prompt model
        meta_model = MetaPromptModel(llm=meta_llm, model_id="system")

        return Context(
            _id=_id, 
            name=name,
            task_prompt_dictator = task_prompt_dictator,
            task_prompt_decider = task_prompt_decider,
            user_prompts=user_prompts,
            assistant_prompts=assistant_prompts,
            meta_prompt=meta_prompt,
            verbose=verbose,
            test_run=test_run,
            buffer=buffer,
            user_models_a=user_models_a,
            user_models_b=user_models_b,
            user_models_c=user_models_c,
            assistant_models=assistant_models, 
            meta_model=meta_model,
            utility=utility,
            n_user_interactions = n_user_interactions,
            n_assistant_interactions = n_assistant_interactions,
        )
    

    def select_players(
            self,
    ) -> tuple:
        """
        Selects the players for the game.
        """

        #generate all possible combinations of user prompts

        user_pairs = list(combinations(self.user_prompts, 2)) + list(combinations(self.user_prompts, 2))[::-1]
        user_pairs = random.sample(user_pairs, self.n_user_interactions)

        #generate all possible combinations of assistant prompts
        assistant_pairs = random.sample(self.assistant_prompts, self.n_assistant_interactions)
        cooperative_pairs = random.sample(self.user_prompts, self.n_assistant_interactions)

        #for assistant prompts, randomly select whether the assistant or the user is dominant

        both_pairs = []
        for s1, s2 in zip(assistant_pairs, cooperative_pairs):
            if random.choice([True, False]):
                both_pairs.append((s1, s2, "assistant_dominant"))
            else:
                both_pairs.append((s2, s1, "user_dominant"))

        return user_pairs, both_pairs


    def run(
        self,
        run: int,
    ) -> None:
        """
        Runs the context, first running user-user interactions and then running user-assistant interactions
        """
        # run user-user interactions
        user_scores_dictator, user_scores_decider, assistant_scores_dictator, assistant_scores_decider = [], [], [], []
        user_pairs, both_pairs = self.select_players()

        # Run user-user interactions and assistant-user interactions at the same
        for (user_model_a, user_model_b, user_pair) in (zip(self.user_models_a, self.user_models_b, user_pairs)):
            # Get the user dictator prompt and the user decider prompt
            dictator_prompt, decider_prompt = user_pair
            
            # get user proposal
            user_a_response = user_model_a.run(buffer=self.buffer, 
                                               user_prompt=dictator_prompt,
                                               task_prompt=self.task_prompt_dictator,
                                               utility=self.utility,
                                               is_dictator=True,
                                               with_assistant=False,
                                               verbose=self.verbose)
            
            # save user proposal
            self.buffer.save_user_context(model_id=f"{user_model_a.model_id}_user_dictator", **user_a_response)
            
            # get user response
            user_b_response = user_model_b.run(buffer=self.buffer,
                                                user_prompt=decider_prompt,
                                                task_prompt=self.task_prompt_decider,
                                                utility=self.utility,
                                                is_dictator=False,
                                                with_assistant=False,
                                                verbose=self.verbose)
            # Get the amounts of money if the proposal was accepted
            if "accept" in user_b_response['response'].lower():
                amount = user_a_response['response'].split('$')
                user_scores_dictator.append(int(amount[1][0]))
                if amount[2][0].isdigit():
                    user_scores_decider.append(int(amount[2][0]))
                else:
                    user_scores_decider.append(int(amount[2][1:3]) - int(amount[2][6]))
            else:
                user_scores_dictator.append(0)
                user_scores_decider.append(0)
            # save user response
            self.buffer.save_user_context(model_id=f"{user_model_b.model_id}_user_decider", **user_b_response)

        # run assistant-user interactions
        for (user_model_c, assistant_model, both_pair) in zip(self.user_models_c, self.assistant_models, both_pairs):
            dictator_prompt, decider_prompt, dominance = both_pair
            # if the assistant is the dictator
            if dominance == "assistant_dominant":
                # get assistant proposal
                assistant_response = assistant_model.run(buffer=self.buffer,
                                                        assistant_prompt=dictator_prompt,
                                                        task_prompt=self.task_prompt_dictator,
                                                        is_dictator=True,
                                                        verbose=self.verbose)           
                # save assistant proposal
                self.buffer.save_assistant_context(model_id=f"{assistant_model.model_id}_assistant_dictator", **assistant_response)

                # get user response
                user_c_response = user_model_c.run(buffer=self.buffer,
                                                        user_prompt= decider_prompt,
                                                        task_prompt=self.task_prompt_decider,
                                                        utility=self.utility,
                                                        is_dictator=False,
                                                        with_assistant=True,
                                                        verbose=self.verbose)
                # Get the amounts of money if the proposal was accepted
                if "accept" in user_c_response['response'].lower():
                    amount = assistant_response['response'].split('$')
                    assistant_scores_dictator.append(int(amount[1][0]))
                else:
                    assistant_scores_dictator.append(0)
                # save user response
                self.buffer.save_user_context(model_id=f"{user_model_c.model_id}_user_dictated_by_assistant", **user_c_response)
            # otherwise, the assistant is the decider
            else:
                # get the user proposal
                user_c_response = user_model_c.run(buffer=self.buffer,
                                            user_prompt=dictator_prompt,
                                            task_prompt=self.task_prompt_dictator,
                                            utility=self.utility,
                                            is_dictator=True,
                                            with_assistant=True,
                                            verbose=self.verbose)
                
                # save user proposal
                self.buffer.save_user_context(model_id=f"{user_model_c.model_id}_user_dictating_assistant", **user_c_response)

                # Get assistant response
                assistant_response = assistant_model.run(buffer=self.buffer,
                                                        assistant_prompt= decider_prompt,
                                                        task_prompt=self.task_prompt_decider,
                                                        is_dictator=False,
                                                        verbose=self.verbose)
                # Get the amounts of money if the proposal was accepted
                if "accept" in assistant_response['response'].lower():
                    amount = user_c_response['response'].split('$')
                    if amount[2][0].isdigit():
                        assistant_scores_decider.append(int(amount[2][0]))
                    else:
                        assistant_scores_decider.append(int(amount[2][1:3]) - int(amount[2][6]))
                else:
                    assistant_scores_decider.append(0)
                # save assistant response
                self.buffer.save_assistant_context(model_id=f"{assistant_model.model_id}_assistant_decider", **assistant_response)
        # run meta-prompt at end of conversation
        meta_response = self.meta_model.run(buffer=self.buffer,
                                            meta_prompt=self.meta_prompt,
                                            task_prompt=self.task_prompt_dictator, 
                                            run=run,
                                            verbose=self.verbose)                 
        # save meta-prompt response for start of next conversation
        self.buffer.save_system_context(model_id="system", **meta_response)
        return user_scores_dictator, user_scores_decider, assistant_scores_dictator, assistant_scores_decider