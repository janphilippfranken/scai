from typing import (
    List, 
    Optional, 
    Any
)


from scai.modules.memory.buffer import CustomConversationBufferWindowMemory
from scai.modules.user.base import UserModel
from scai.modules.assistant.base import AssistantModel
from scai.modules.meta_prompt.base import MetaPromptModel


class Episode():
    def __init__(self, id: str, name: str, task_prompt: str, user_prompts: List[str], assistant_prompts: List[str], meta_prompt: str,
                 buffer: CustomConversationBufferWindowMemory, user_models: List[UserModel], 
                 assistant_models: List[AssistantModel], meta_model: MetaPromptModel):
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

    @staticmethod
    def create(id: str, name: str, task_prompt: str, user_prompts: List[str], assistant_prompts: List[str], meta_prompt: str,
               n_user: int, user_llm: Any, n_assistant: int, assistant_llm: Any, meta_llm: Any, 
               adjacency_matrix: Optional[Any] = None, system_k: int = 5, chat_k: int = 5, 
               user_k: int = 5, assistant_k: int = 5, assistant_system_k: int = 1) -> "Episode":
        buffer = CustomConversationBufferWindowMemory(system_k=system_k, chat_k=chat_k, user_k=user_k, 
                                                      assistant_k=assistant_k,
                                                      assistant_system_k=assistant_system_k)
        user_models = [UserModel(llm=user_llm, conversation_id=str(conversation_id)) for conversation_id in range(n_user)]
        assistant_models = [AssistantModel(llm=assistant_llm, conversation_id=str(conversation_id)) for conversation_id in range(n_assistant)]
        meta_model = MetaPromptModel(llm=meta_llm)

        return Episode(id, name, task_prompt, user_prompts, assistant_prompts, meta_prompt, buffer, user_models, assistant_models, meta_model)

    def run(self) -> CustomConversationBufferWindowMemory:
        for assistant_model, assistant_prompt, user_model, user_prompt in zip(self.assistant_models, self.assistant_prompts, self.user_models, self.user_prompts):
            assistant_response = assistant_model.run(assistant_prompt=assistant_prompt, task_prompt=self.task_prompt, buffer=self.buffer)
            self.buffer.save_context(assistant={"content": assistant_response}, assistant_message_id="conversation_" + str(assistant_model.conversation_id) + "_assistant")
            user_response = user_model.run(user_prompt=user_prompt, task_prompt=self.task_prompt, buffer=self.buffer)
            self.buffer.save_context(user={"content": user_response}, user_message_id="conversation_" + str(user_model.conversation_id) + "_user")

        meta_response = self.meta_model.run(meta_prompt=self.meta_prompt, task_prompt=self.task_prompt, buffer=self.buffer)
        self.buffer.save_context(system={"content": meta_response}, system_message_id="system_message_1")

        return self.buffer