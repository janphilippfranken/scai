from typing import (
    List, 
    Optional, 
    Any,
    Dict,
)

from scai.agents.user import UserModel
from scai.agents.assistant import AssistantModel
from scai.agents.meta_prompt import MetaPromptModel

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
        assistant_models: List[AssistantModel], 
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
            meta_prompt: meta-prompt template
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
        assistant_llm: AssistantModel, 
        meta_llm: MetaPromptModel, 
        id: str, 
        name: str, 
        task_prompt: str, 
        user_prompts: List[str], 
        assistant_prompts: List[str], 
        meta_prompt: str, 
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
        user_models = [UserModel(llm=user_llm, conversation_id=str(conversation_id), k=chat_k) for conversation_id, _ in enumerate(user_prompts)]
        assistant_models = [AssistantModel(llm=assistant_llm, conversation_id=str(conversation_id), k=chat_k, system_k=system_k) for conversation_id, _ in enumerate(assistant_prompts)]
        meta_model = MetaPromptModel(llm=meta_llm, conversation_id="system", k=system_k)

        return Context(
            id=id, 
            name=name,
            task_prompt=task_prompt,
            user_prompts=user_prompts,
            assistant_prompts=assistant_prompts,
            meta_prompt=meta_prompt,
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

    def run(self) -> ConversationBuffer:
        assert len(self.assistant_models) == len(self.assistant_prompts), "Mismatch between assistant models and prompts"
        assert len(self.user_models) == len(self.user_prompts), "Mismatch between user models and prompts"

        for assistant_model, assistant_prompt, user_model, user_prompt in zip(self.assistant_models, self.assistant_prompts, self.user_models, self.user_prompts):
            
            # run assistant model
            assistant_response = assistant_model.run(assistant_prompt=assistant_prompt, 
                                                     task_prompt=self.task_prompt, 
                                                     user_prompt=user_prompt,
                                                     buffer=self.buffer,
                                                     verbose=self.verbose,
                                                     test_run=self.test_run,
                                                     max_tokens=self.max_tokens_assistant)
            # save assistant response
            self.buffer.save_assistant_context(message_id=f"{assistant_model.conversation_id}_assistant", **assistant_response)
            
            # run user model
            user_response = user_model.run(user_prompt=user_prompt, 
                                           task_prompt=self.task_prompt, 
                                           metric_prompt=self.metric_prompt,
                                           buffer=self.buffer,
                                           verbose=self.verbose,
                                           test_run=self.test_run,
                                           max_tokens=self.max_tokens_user)
            # save user response
            self.buffer.save_user_context(message_id=f"{user_model.conversation_id}_user", **user_response)

        # run meta-prompt
        meta_response = self.meta_model.run(meta_prompt=self.meta_prompt, 
                                            task_prompt=self.task_prompt, 
                                            buffer=self.buffer,
                                            verbose=self.verbose,
                                            test_run=self.test_run,
                                            max_tokens=self.max_tokens_meta,
                                            max_tokens_assistant=self.max_tokens_assistant)
        # save meta-prompt response
        self.buffer.save_system_context(message_id="system", **meta_response)
        
        return self.buffer