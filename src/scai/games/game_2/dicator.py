from typing import List


from scai.games.game_2.agents.user import UserModel
from scai.games.game_2.agents.assistant import AssistantAgent
from scai.games.game_2.agents.meta import MetaPromptModel

from scai.memory.buffer import ConversationBuffer

class Context():
    def __init__(
        self, 
        _id: str,
        name: str, 
        task_prompt: str, 
        user_prompts: List[str], 
        assistant_prompts: List[str], 
        meta_prompt: str, 
        buffer: ConversationBuffer, 
        user_models: List[UserModel], 
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
        self.task_prompt = task_prompt
        self.user_prompts = user_prompts
        self.assistant_prompts = assistant_prompts
        self.meta_prompt = meta_prompt
        self.verbose = verbose
        # run settings
        self.test_run = test_run
        # models and buffer
        self.buffer = buffer
        self.user_models = user_models
        self.assistant_models = assistant_models
        self.meta_model = meta_model

    @staticmethod
    def create(
        user_llm: UserModel, 
        assistant_llm: AssistantAgent, 
        meta_llm: MetaPromptModel, 
        _id: str, 
        name: str, 
        task_prompt: str, 
        user_prompts: List[str], 
        assistant_prompts: List[str], 
        meta_prompt: str,
        verbose: bool,
        test_run: bool,
    ) -> "Context":
        """
        Creates a context (i.e. context for the MDP / Meta-Prompt run).
        """
        # buffer for storing conversation history
        buffer = ConversationBuffer()
        # user models
        user_models = [
            UserModel(llm=user_llm, model_id=str(model_id)) for model_id, _ in enumerate(user_prompts)
            ]
        # assistant models 
        assistant_models = [
            AssistantAgent(llm=assistant_llm, model_id=str(model_id)) for model_id, _ in enumerate(assistant_prompts)
            ]
        # meta prompt model
        meta_model = MetaPromptModel(llm=meta_llm, model_id="system")

        return Context(
            _id=_id, 
            name=name,
            task_prompt=task_prompt,
            user_prompts=user_prompts,
            assistant_prompts=assistant_prompts,
            meta_prompt=meta_prompt,
            verbose=verbose,
            test_run=test_run,
            buffer=buffer,
            user_models=user_models,
            assistant_models=assistant_models, 
            meta_model=meta_model,
        )

    def run(
        self,
        run: int,
    ) -> None:
        
        assert len(self.assistant_models) == len(self.assistant_prompts), "Mismatch between assistant models and prompts"
        assert len(self.user_models) == len(self.user_prompts), "Mismatch between user models and prompts"


        """
        What we need to do:
        Make a randomized selection function that selects users/assistants
        Based on the parameters in the yaml file, make however many user-user interaction and however many user-assistant interaction pairs
        Run the user-user interactions, then run the assistant-assistant interaction pairs
        Change the parameters of context and main to reflect the parameters in the yaml file
        When running dictator and decider, make sure to pass in the appropriate parameters
        Debug
        Clean up code
        Expand on code to be more flexible to more use cases:
            Add buffer back in to allow for multiple turns
            Make sure that the original game works
            Try to reuse code wherever possible - no modifications to base or memory were made - we can move these files so redundant code isn't used
        """
        for assistant_model, assistant_prompt, user_model, user_prompt \
            in zip(self.assistant_models, self.assistant_prompts, self.user_models, self.user_prompts):

            # get assistant response
            assistant_response = assistant_model.run_dictator(buffer=self.buffer,
                                                     assistant_prompt=assistant_prompt,
                                                     task_prompt=self.task_prompt,
                                                     verbose=self.verbose)

            assistant_response = assistant_model.run_decider(buffer=self.buffer,
                                                     assistant_prompt=assistant_prompt,
                                                     task_prompt=self.task_prompt,
                                                     verbose=self.verbose)
            # save assistant response
            self.buffer.save_assistant_context(model_id=f"{assistant_model.model_id}_assistant", **assistant_response)
            
            # get user response
            user_response = user_model.run_dictator(buffer=self.buffer,
                                           user_prompt=user_prompt,
                                           task_prompt=self.task_prompt,
                                           utility=None,
                                           verbose=self.verbose)
            
            # get user response
            user_response = user_model.run_decider(buffer=self.buffer,
                                           user_prompt=user_prompt,
                                           task_prompt=self.task_prompt,
                                           utility=None,
                                           verbose=self.verbose)
            # save user response
            self.buffer.save_user_context(model_id=f"{user_model.model_id}_user", **user_response)
        
        # run meta-prompt at end of conversation
        meta_response = self.meta_model.run(buffer=self.buffer,
                                            meta_prompt=self.meta_prompt,
                                            task_prompt=self.task_prompt, 
                                            metric_prompt=self.metric_prompt,
                                            run=run,
                                            verbose=self.verbose,
                                            max_tokens_meta=self.max_tokens_meta,
                                            max_tokens_assistant=self.max_tokens_assistant)                 
        # save meta-prompt response for start of next conversation
        self.buffer.save_system_context(model_id="system", **meta_response)