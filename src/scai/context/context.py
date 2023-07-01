from typing import (
    List, 
    Optional, 
    Any
)


from scai.memory.buffer import ConversationBuffer
from scai.user.base import UserModel
from scai.assistant.base import AssistantModel
from scai.meta_prompt.base import MetaPromptModel


class Context():
    def __init__(
        self, id: str, name: str, task_prompt: str, user_prompts: List[str], assistant_prompts: List[str], meta_prompt: str,
        buffer: ConversationBuffer, user_models: List[UserModel], 
        assistant_models: List[AssistantModel], meta_model: MetaPromptModel, verbose: bool, test_run: bool,
    ) -> None:
        """
        Initializes an context (i.e. context for the MDP / Meta-Prompt run).

        Args:

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
        n_user: int, user_llm: Any, n_assistant: int, assistant_llm: Any, meta_llm: Any, 
        adjacency_matrix: Optional[Any] = None, system_k: int = 5, chat_k: int = 5, verbose: bool = False, test_run: bool = True,
    ) -> "Context":
        """
        Creates a context (i.e. context for the MDP / Meta-Prompt run).
        
        Args:
           
        Returns:
        """
        # create buffer
        buffer = ConversationBuffer(system_k=system_k, chat_k=chat_k)
        # create models
        user_models = [UserModel(llm=user_llm, conversation_id=str(conversation_id + 1)) for conversation_id in range(n_user)]
        assistant_models = [AssistantModel(llm=assistant_llm, conversation_id=str(conversation_id + 1)) for conversation_id in range(n_assistant)]
        meta_model = MetaPromptModel(llm=meta_llm)

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

    def run(
        self,
    ) -> ConversationBuffer:

        for assistant_model, assistant_prompt, user_model, user_prompt in zip(self.assistant_models, self.assistant_prompts, self.user_models, self.user_prompts):
            
            # run asssistant model
            assistant_response = assistant_model.run(assistant_prompt=assistant_prompt, 
                                                     task_prompt=self.task_prompt, 
                                                     buffer=self.buffer,
                                                     verbose=self.verbose,
                                                     test_run=self.test_run)
            # save assistant response
            self.buffer.save_assistant_context(assistant_message_id="conversation_" + str(assistant_model.conversation_id) + "_assistant", **assistant_response)
            
            # run user model
            user_response = user_model.run(user_prompt=user_prompt, 
                                           task_prompt=self.task_prompt, 
                                           buffer=self.buffer,
                                           verbose=self.verbose,
                                           test_run=self.test_run)
            # save user response
            self.buffer.save_user_context(user_message_id="conversation_" + str(user_model.conversation_id) + "_user", **user_response)

        # run meta-prompt
        meta_response = self.meta_model.run(meta_prompt=self.meta_prompt, 
                                            task_prompt=self.task_prompt, 
                                            buffer=self.buffer,
                                            verbose=self.verbose,
                                            test_run=self.test_run)
        # save meta-prompt response
        self.buffer.save_meta_context(meta_message_id="meta_prompt", **meta_response)
        
        return self.buffer