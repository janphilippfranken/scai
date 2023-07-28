from typing import List


from scai.games.game_2.agents.user import UserModel
from scai.games.game_2.agents.assistant import AssistantAgent
from scai.games.game_2.agents.meta import MetaPromptModel

from scai.games.dictator_games.all_prompts.user_model import UserPrompt
from scai.games.dictator_games.all_prompts.assistant_model import AssistantPrompt



from scai.memory.buffer import ConversationBuffer
import re
import random
from itertools import combinations

class Context():
    def __init__(
        user_llm: UserModel,
        assistant_llm: AssistantAgent,
        meta_llm: MetaPromptModel,
        self, 
        _id: str,
        name: str, 
        task_prompt_dictator: str, 
        task_prompt_decider: str,
        user_prompts: List[str], 
        assistant_prompts: List[str], 
        meta_prompt: str, 
        buffer: ConversationBuffer, 
        meta_model: MetaPromptModel, 
        verbose: bool, 
        test_run: bool,
        n_fixed_inter : int,
        n_mixed_inter : int,
        n_flex_inter : int,
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
        self.meta_model = meta_model
        self.n_fixed_inter = n_fixed_inter,
        self.n_mixed_inter = n_mixed_inter,
        self.n_flex_inter = n_flex_inter,
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
        user_prompts: List[str], 
        assistant_prompts: List[str], 
        meta_prompt: str,
        verbose: bool,
        test_run: bool,
        n_fixed_inter : int,
        n_mixed_inter : int,
        n_flex_inter : int,
    ) -> "Context":
        """
        Creates a context (i.e. context for the MDP / Meta-Prompt run).
        """
        # buffer for storing conversation history
        buffer = ConversationBuffer()
        # meta prompt model
        meta_model = MetaPromptModel(llm=meta_llm, model_id="system")

        return Context(
            user_llm = user_llm,
            assistant_llm = assistant_llm,
            meta_llm = meta_llm,
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
            meta_model=meta_model,
            n_fixed_inter = n_fixed_inter,
            n_mixed_inter = n_mixed_inter,
            n_flex_inter = n_flex_inter,
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
        for i, (s1, s2) in enumerate(zip(assistant_pairs, cooperative_pairs)):
            if i & 1 == 0:
                both_pairs.append((s1, s2, "assistant_dominant"))
            else:
                both_pairs.append((s2, s1, "user_dominant"))

        return user_pairs, both_pairs

    def get_money(
        self, 
        index: int,
        dictator_str: str, 
        decider_str: str,  
        dictator_scores: list,
        decider_scores: list,
        proposals: list,
        user: bool,
        assistant_dominant: bool
    ) -> None:
        amount = dictator_str['response'].split('$')
        dictator_money = re.search(r'\d+', amount[1]).group()
        decider_money = re.search(r'\d+', amount[2]).group()
        dictator_money, decider_money = int(dictator_money), int(decider_money)
        if user or assistant_dominant:
            proposals.append((dictator_money, decider_money))
        accept = 1 if "accept" in decider_str['response'].lower() else 0
        if accept:
            if user:
                dictator_scores[index] = dictator_money
                decider_scores[index] = decider_money
            elif assistant_dominant:
                dictator_scores[index] = dictator_money
            else:
                decider_scores[index] = decider_money

    # takes in a list of paired prompts
    # returns list with tuples structured as this: (prompt_dictator, model_dictator, prompt_decider, model_decider, "dictator", "decider")
    def pair_models_with_prompts(
        self,
        user_llm: UserModel, 
        assistant_llm: AssistantAgent, 
        prompt_pairs: list[tuple],
    ) -> List:
        
        pairs = []
        for (prompt_dictator, prompt_decider) in prompt_pairs:
            pair = [prompt_dictator, prompt_decider]
            if type(prompt_dictator) == UserPrompt:
                model_dictator = UserModel(llm=user_llm, model_id=str(0)) # TODO: change model_id
                pair.append("fixed_dictator")
            else:
                model_dictator = AssistantAgent(llm=assistant_llm, model_id=str(0))
                pair.append("flex_dictator")
            pair.insert(1, model_dictator)
            if type(prompt_decider) == UserPrompt:
                model_decider = UserModel(llm=user_llm, model_id=str(1))
                pair.append("fixed_decider")
            else:
                model_decider = AssistantAgent(llm=assistant_llm, model_id=str(1))
                pair.append("flex_decider")
            pair.insert(3, model_decider)
            pairs.append(pair)
        return pairs


    #TODO: Reconcile Run branches or modeify GetMoney to work with all

    def run(
        self,
        run: int,
        pairs: list[tuple],
    ) -> None:
        
        user_proposals, user_scores_dictator, user_scores_decider = [], [0] * self.n_user_interactions, [0] * self.n_user_interactions
        assistant_proposals, assistant_scores_dictator, assistant_scores_decider = [], [0] * self.n_assistant_interactions, [0] * self.n_assistant_interactions
        
        for i, pair in enumerate(pairs):

            prompt_dictator, model_dictator, prompt_decider, model_decider, dictator, decider = pair

            #run interaction
            if dictator == "fixed_dictator":
                if decider == "fixed_decider":
                    run_fixed_fixed(prompt_dictator, model_dictator, prompt_decider, model_decider)
                else:
                    run_fixed_flex(prompt_dictator, model_dictator, prompt_decider, model_decider)
            else:
                if decider == "fixed_decider":
                    run_flex_fixed(prompt_dictator, model_dictator, prompt_decider, model_decider)
                else:
                    run_flex_flex(prompt_dictator, model_dictator, prompt_decider, model_decider)

            self.get_money(i, dictator_response, decider_response, assistant_scores_dictator, assistant_scores_decider, [], False, False)

            
        # run meta-prompt at end of conversation
        meta_response = self.meta_model.run(buffer=self.buffer,
                                            meta_prompt=self.meta_prompt,
                                            task_prompt=self.task_prompt_dictator, 
                                            run=run,
                                            verbose=self.verbose)                 
        # save meta-prompt response for start of next conversation
        self.buffer.save_system_context(model_id="system", **meta_response)
        return user_scores_dictator, user_scores_decider, assistant_scores_dictator, assistant_scores_decider, user_proposals, assistant_proposals


        
        
    def run_fixed_fixed(
            self,
            prompt_dictator,
            model_dictator,
            prompt_decider,
            model_decider,
    ) -> None:
        
        # get user proposal
        dictator_response = model_dictator.run(buffer=self.buffer, 
                                            user_prompt=prompt_dictator,
                                            task_prompt=self.task_prompt_dictator,
                                            utility=self.utility,
                                            is_dictator=True,
                                            with_assistant=False,
                                            verbose=self.verbose)
        
        # save user proposal
        self.buffer.save_user_context(model_id=f"{model_dictator.model_id}_user_dictator", **dictator_response)
        
        # get user response
        decider_response = model_decider.run(buffer=self.buffer,
                                            user_prompt=prompt_decider,
                                            task_prompt=self.task_prompt_decider,
                                            utility=self.utility,
                                            is_dictator=False,
                                            with_assistant=False,
                                            verbose=self.verbose)
        
        # save user response
        self.buffer.save_user_context(model_id=f"{model_decider.model_id}_user_decider", **decider_response)
        
        return dictator_response, decider_response
    
    def run_fixed_flex(
            self,
            prompt_dictator,
            model_dictator,
            prompt_decider,
            model_decider,
    ) -> None:
        
        # get user proposal
        dictator_response = model_dictator.run(buffer=self.buffer, 
                                            user_prompt=prompt_dictator,
                                            task_prompt=self.task_prompt_dictator,
                                            utility=self.utility,
                                            is_dictator=True,
                                            with_assistant=False,
                                            verbose=self.verbose)
        
        # save user proposal
        self.buffer.save_user_context(model_id=f"{model_dictator.model_id}_user_dictator", **dictator_response)
        
        # get assistant response
        decider_response = model_decider.run(buffer=self.buffer,
                                            assistant_prompt=prompt_decider,
                                            task_prompt=self.task_prompt_decider,
                                            is_dictator=False,
                                            verbose=self.verbose)
        
        # save assistant response
        self.buffer.save_user_context(model_id=f"{model_decider.model_id}_user_decider", **decider_response)
        
        return dictator_response, decider_response
    
    def run_flex_fixed(
            self,
            prompt_dictator,
            model_dictator,
            prompt_decider,
            model_decider,
    ) -> None:
        
        # get assistant proposal
        dictator_response = model_dictator.run(buffer=self.buffer, 
                                            assistant_prompt=prompt_dictator,
                                            task_prompt=self.task_prompt_dictator,
                                            is_dictator=True,
                                            verbose=self.verbose)
        
        # save assistant proposal
        self.buffer.save_user_context(model_id=f"{model_dictator.model_id}_user_dictator", **dictator_response)
        
        # get user response
        decider_response = model_decider.run(buffer=self.buffer,
                                            user_prompt=prompt_decider,
                                            task_prompt=self.task_prompt_decider,
                                            utility=self.utility,
                                            is_dictator=False,
                                            with_assistant=False,
                                            verbose=self.verbose)
        
        # save user response
        self.buffer.save_user_context(model_id=f"{model_decider.model_id}_user_decider", **decider_response)
        
        return dictator_response, decider_response
    
    def run_flex_flex(
            self,
            prompt_dictator,
            model_dictator,
            prompt_decider,
            model_decider,
    ) -> None:
        
        # get assistant proposal
        dictator_response = model_dictator.run(buffer=self.buffer, 
                                            assistant_prompt=prompt_dictator,
                                            task_prompt=self.task_prompt_dictator,
                                            is_dictator=True,
                                            verbose=self.verbose)
        
        # save assistant proposal
        self.buffer.save_user_context(model_id=f"{model_dictator.model_id}_user_dictator", **dictator_response)
        
        # get assistant response
        decider_response = model_decider.run(buffer=self.buffer,
                                            assistant_prompt=prompt_decider,
                                            task_prompt=self.task_prompt_decider,
                                            is_dictator=False,
                                            verbose=self.verbose)
        
        # save assistant response
        self.buffer.save_user_context(model_id=f"{model_decider.model_id}_user_decider", **decider_response)
        
        return dictator_response, decider_response