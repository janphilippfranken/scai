from typing import (
    List, 
    Optional, 
    Any
)


from scai.modules.memory.buffer import CustomConversationBufferWindowMemory
from scai.modules.user.base import UserModel
from scai.modules.assistant.base import AssistantModel
from scai.modules.meta_prompt.base import MetaPromptModel


class Context():
    def __init__(
        self, id: str, name: str, task_prompt: str, user_prompts: List[str], assistant_prompts: List[str], meta_prompt: str,
        buffer: CustomConversationBufferWindowMemory, user_models: List[UserModel], 
        assistant_models: List[AssistantModel], meta_model: MetaPromptModel, verbose: bool, test_run: bool,
    ) -> None:
        """
        Initializes an context (i.e. context for the MDP / Meta-Prompt run).

        Args:
            id: The unique identifier for the context.
            name: The name of the context.
            task_prompt: The task prompt for the context.
            user_prompts: The user prompts for the context.
            assistant_prompts: The assistant prompts for the context.
            meta_prompt: The meta prompt for the context.
            buffer: The buffer containing the conversation history.
            user_models: The user models for the context.
            assistant_models: The assistant models for the context.
            meta_model: The meta model for the context.
            verbose: Whether to print out the context information.
            test_run: Whether we just want to simulate a response


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
        adjacency_matrix: Optional[Any] = None, system_k: int = 5, chat_k: int = 5, 
        user_k: int = 5, assistant_k: int = 5, assistant_system_k: int = 1, verbose: bool = False, test_run: bool = True,
    ) -> "Context":
        """
        Creates a context (i.e. context for the MDP / Meta-Prompt run).
        
        Args:
            id: The unique identifier for the context.
            name: The name of the context.
            task_prompt: The task prompt for the context.
            user_prompts: The user prompts for the context.
            assistant_prompts: The assistant prompts for the context.
            meta_prompt: The meta prompt for the context.
            n_user: The number of users in the context.
            user_llm: The user LLM.
            n_assistant: The number of assistants in the context.
            assistant_llm: The assistant LLM.
            meta_llm: The meta LLM.
            adjacency_matrix: The adjacency matrix for the context.
            system_k: The number of system messages to include in the context.
            chat_k: The number of chat messages to include in the context.
            user_k: The number of user messages to include in the context.
            assistant_k: The number of assistant messages to include in the context.
            assistant_system_k: The number of assistant system messages to include in the context.
            verbose: Whether to print out the context information.
            test_run: Whether we just want to simulate a response
            
        Returns:
            Context
        """
        # TODO: implement mechanism for communication between users and assistants (adjacency matrix)
        # create buffer
        buffer = CustomConversationBufferWindowMemory(system_k=system_k, chat_k=chat_k, user_k=user_k, 
                                                      assistant_k=assistant_k,
                                                      assistant_system_k=assistant_system_k)
        
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
    ) -> CustomConversationBufferWindowMemory:

        # TODO: make this more general. 1) different numbers of users vs assistants, 2) users should be able to communicate with each other, 3) more elegant way to handle unique identifiers
        for assistant_model, assistant_prompt, user_model, user_prompt in zip(self.assistant_models, self.assistant_prompts, self.user_models, self.user_prompts):
            
            # run asssistant model
            assistant_response = assistant_model.run(assistant_prompt=assistant_prompt, 
                                                     task_prompt=self.task_prompt, 
                                                     buffer=self.buffer,
                                                     verbose=self.verbose,
                                                     test_run=self.test_run)
            # save assistant response
            self.buffer.save_context(assistant={"content": assistant_response['Response']}, 
                                     assistant_rating=None,
                                     assistant_prompt=assistant_response['Prompt'],
                                     assistant_message_id="conversation_" + str(assistant_model.conversation_id) + "_assistant")
            
            # run user model
            user_response = user_model.run(user_prompt=user_prompt, 
                                           task_prompt=self.task_prompt, 
                                           buffer=self.buffer,
                                           verbose=self.verbose,
                                           test_run=self.test_run)
            # save user response
            self.buffer.save_context(user={"content": user_response['Feedback']}, 
                                     user_rating=user_response['Rating'], 
                                     user_prompt=user_response['Prompt'],
                                     user_message_id="conversation_" + str(user_model.conversation_id) + "_user")

        # run meta-prompt
        meta_response = self.meta_model.run(meta_prompt=self.meta_prompt, 
                                            task_prompt=self.task_prompt, 
                                            buffer=self.buffer,
                                            verbose=self.verbose,
                                            test_run=self.test_run)
        # save meta-prompt response
        self.buffer.save_context(system={"content": meta_response['System Message']}, 
                                 system_rating=meta_response['Critique'], 
                                 system_prompt=meta_response['Prompt'], 
                                 system_message_id="system_message_0")
        
        return self.buffer