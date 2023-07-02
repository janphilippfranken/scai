from typing import (
    List, 
    Optional, 
    Any,
    Dict,
)

from scai.user.base import UserModel
from scai.assistant.base import AssistantModel
from scai.meta_prompt.base import MetaPromptModel

from scai.memory.buffer import ConversationBuffer

class Context():
    def __init__(
        self, id: str, name: str, task_prompt: str, user_prompts: List[str], assistant_prompts: List[str], meta_prompt: str,
        buffer: ConversationBuffer, user_models: List[UserModel], 
        assistant_models: List[AssistantModel], meta_model: MetaPromptModel, verbose: bool, test_run: bool,
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
            user_llm: A UserModel object.
            assistant_llm: assistant model
            meta_llm: meta-prompt model
            adjacency_matrix: connectivity matrix for the user and assistant models.
            system_k: system memory length
            chat_k: chat memory length
            verbose: whether to run in verbose mode.
            test_run:  whether it is a test run.

        Returns:
            None
        """
        self.id = id
        self.name = name
        self.task_prompt = task_prompt
        self.user_prompts = user_prompts
        self.assistant_prompts = assistant_prompts
        self.meta_prompt = meta_prompt
        self.buffer = buffer
        self.user_models = user_models
        self.assistant_models = assistant_models
        self.meta_model = meta_model
        self.verbose = verbose
        self.test_run = test_run

    @staticmethod
    def create(
        id: str, name: str, task_prompt: str, user_prompts: List[str], assistant_prompts: List[str], meta_prompt: str,
        user_llm: UserModel, assistant_llm: AssistantModel, meta_llm: MetaPromptModel, 
        adjacency_matrix: Optional[Dict] = None, system_k: int = 5, chat_k: int = 5, verbose: bool = False, test_run: bool = True,
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
            id, 
            name, 
            task_prompt, 
            user_prompts, 
            assistant_prompts, 
            meta_prompt, 
            buffer, 
            user_models, 
            assistant_models, 
            meta_model, 
            verbose,
            test_run,
        )

    def run(self) -> ConversationBuffer:
        assert len(self.assistant_models) == len(self.assistant_prompts), "Mismatch between assistant models and prompts"
        assert len(self.user_models) == len(self.user_prompts), "Mismatch between user models and prompts"

        for assistant_model, assistant_prompt, user_model, user_prompt in zip(self.assistant_models, self.assistant_prompts, self.user_models, self.user_prompts):
            
            # run assistant model
            assistant_response = assistant_model.run(assistant_prompt=assistant_prompt, 
                                                     task_prompt=self.task_prompt, 
                                                     buffer=self.buffer,
                                                     verbose=self.verbose,
                                                     test_run=self.test_run)
            # save assistant response
            self.buffer.save_assistant_context(message_id=f"{assistant_model.conversation_id}_assistant", **assistant_response)
            
            # run user model
            user_response = user_model.run(user_prompt=user_prompt, 
                                           task_prompt=self.task_prompt, 
                                           buffer=self.buffer,
                                           verbose=self.verbose,
                                           test_run=self.test_run)
            # save user response
            self.buffer.save_user_context(message_id=f"{user_model.conversation_id}_user", **user_response)

        # run meta-prompt
        meta_response = self.meta_model.run(meta_prompt=self.meta_prompt, 
                                            task_prompt=self.task_prompt, 
                                            buffer=self.buffer,
                                            verbose=self.verbose,
                                            test_run=self.test_run)
        # save meta-prompt response
        self.buffer.save_system_context(message_id="system", **meta_response)
        
        return self.buffer