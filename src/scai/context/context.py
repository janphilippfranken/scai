from typing import (
    List, 
    Optional, 
    Any,
    Dict,
)

from scai.agents.user import UserModel
from scai.agents.assistant import AssistantAgent
from scai.agents.meta import MetaPromptModel

from scai.memory.buffer import ConversationBuffer

class Context():
    def __init__(
        self, 
        id: str,
        name: str, 
        task_prompt: str, 
        user_prompts: List[str], 
        assistant_prompts: List[str], 
        meta_prompt: str, 
        metric_prompt: str,
        buffer: ConversationBuffer, 
        user_models: List[UserModel], 
        assistant_models: List[AssistantAgent], 
        meta_model: MetaPromptModel, 
        verbose: bool, 
        test_run: bool, 
        max_tokens_user: int,
        max_tokens_assistant: int,
        max_tokens_meta: int,
    ) -> None:
        """
        Initializes a context (i.e. context for the MDP / Meta-Prompt run).

        Args:
            id: unique identifier for the context.
            name: name of the context.
            task_prompt: task prompt template
            user_prompts: user prompt templates
            assistant_prompts: assistant prompt templates
            meta: meta-prompt template
            metric_prompt: metric-prompt template
            adjacency_matrix: connectivity matrix for the user and assistant models. # TODO: add
            system_k: system memory length
            chat_k: chat memory length
            verbose: whether to run in verbose mode.
            test_run:  whether it is a test run.
            max_tokens_user: maximum number of tokens for user model.
            max_tokens_assistant: maximum number of tokens for assistant model.
            max_tokens_meta: maximum number of tokens for meta-prompt model.
            buffer: conversation buffer
            user_llm: A UserModel object.
            assistant_llm: assistant model
            meta_llm: meta-prompt model

        Returns:
            None
        """
        self.id = id
        self.name = name
        self.task_prompt = task_prompt
        self.user_prompts = user_prompts
        self.assistant_prompts = assistant_prompts
        self.meta_prompt = meta_prompt
        self.metric_prompt = metric_prompt
        self.verbose = verbose
        self.test_run = test_run
        self.max_tokens_user = max_tokens_user
        self.max_tokens_assistant = max_tokens_assistant
        self.max_tokens_meta = max_tokens_meta
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
        id: str, 
        name: str, 
        task_prompt: str, 
        user_prompts: List[str], 
        assistant_prompts: List[str], 
        meta: str, 
        metric_prompt: str,
        system_k: int,
        chat_k: int,
        verbose: bool,
        test_run: bool,
        max_tokens_user: int,
        max_tokens_assistant: int,
        max_tokens_meta: int,
    ) -> "Context":
        """
        Creates a context (i.e. context for the MDP / Meta-Prompt run).
        """
        # create buffer
        buffer = ConversationBuffer()
        # create models
        user_models = [UserModel(llm=user_llm, model_id=str(model_id)) for model_id, _ in enumerate(user_prompts)]
        assistant_models = [AssistantAgent(llm=assistant_llm, model_id=str(model_id)) for model_id, _ in enumerate(assistant_prompts)]
        meta_model = MetaPromptModel(llm=meta_llm, model_id="system")

        return Context(
            id=id, 
            name=name,
            task_prompt=task_prompt,
            user_prompts=user_prompts,
            assistant_prompts=assistant_prompts,
            meta=meta,
            metric_prompt=metric_prompt,
            verbose=verbose,
            test_run=test_run,
            max_tokens_user=max_tokens_user,
            max_tokens_assistant=max_tokens_assistant,
            max_tokens_meta=max_tokens_meta,
            buffer=buffer,
            user_models=user_models,
            assistant_models=assistant_models, 
            meta_model=meta_model,
        )

    def run_chat(
        self,
        turn: int,
    ) -> ConversationBuffer:
        """
        Runs one turn of each conversation.

        Args:
            turn: turn number
        """
        assert len(self.assistant_models) == len(self.assistant_prompts), "Mismatch between assistant models and prompts"
        assert len(self.user_models) == len(self.user_prompts), "Mismatch between user models and prompts"

        for assistant_model, assistant_prompt, user_model, user_prompt in zip(self.assistant_models, self.assistant_prompts, self.user_models, self.user_prompts):
            
            # run assistant model
            assistant_response = assistant_model.run(buffer=self.buffer,
                                                     assistant_prompt=assistant_prompt,
                                                     task_prompt=self.task_prompt, 
                                                     turn=turn,
                                                     test_run=self.test_run,
                                                     verbose=self.verbose,
                                                     max_tokens=self.max_tokens_assistant)
                
                
            # save assistant response
            self.buffer.save_assistant_context(model_id=f"{assistant_model.model_id}_assistant", **assistant_response)
            
            # run user model
            user_response = user_model.run(buffer=self.buffer,
                                           user_prompt=user_prompt,
                                           task_prompt=self.task_prompt,
                                           metric_prompt=self.metric_prompt,
                                           turn=turn,
                                           test_run=self.test_run,
                                           verbose=self.verbose,
                                           max_tokens=self.max_tokens_user)
            # save user response
            self.buffer.save_user_context(model_id=f"{user_model.model_id}_user", **user_response)

    def run(
        self, 
        n_turns: int,
    ) -> None:
        # run meta-prompt
        for turn in range(n_turns):
            self.run_chat(turn)
            
        meta_response = self.meta_model.run(buffer=self.buffer,
                                            meta_prompt=self.meta_prompt 
                                            task_prompt=self.task_prompt, 
                                            turn=turn,
                                            test_run=self.test_run,
                                            verbose=self.verbose,
                                            max_tokens_meta=self.max_tokens_meta,
                                            max_tokens_assistant=self.max_tokens_assistant)
        # save meta-prompt response
        self.buffer.save_system_context(model_id="system", **meta_response)