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
    
    def __init__(self, 
                 id: str, 
                 name: str, 
                 n_user: int,
                 user_llm: Any, 
                 n_assistant: int,
                 assistant_llm: Any,
                 meta_llm: Any,
                 adjacency_matrix: Optional[Any]=None, 
                 system_k: int=5, 
                 chat_k: int=5, 
                 user_k: int=5, 
                 assistant_k: int=5, 
                 assistant_system_k: int=1
    ):
        self.id = id
        self.name = name
        self.buffer = CustomConversationBufferWindowMemory(system_k=system_k, 
                                                      chat_k=chat_k, 
                                                      user_k=user_k, 
                                                      assistant_k=assistant_k,
                                                      assistant_system_k=assistant_system_k)
        self.user_models = [UserModel(llm=user_llm, conversation_id=conversation_id) for conversation_id in range(n_user)]
        self.assistant_models = [AssistantModel(llm=assistant_llm, conversation_id=conversation_id) for conversation_id in range(n_assistant)]
        self.meta_model = MetaPromptModel(llm=meta_llm)
        self.adjacency_matrix = adjacency_matrix

    def run(self,
            task_prompt: str,
            assistant_prompt: str, # the thing that should change
            user_prompt: str,
            meta_prompt: str,
    ) -> CustomConversationBufferWindowMemory:
        
        for assistant_model, user_model in zip(self.assistant_models, self.user_models):
            assistant_response = assistant_model.run(assistant_prompt=assistant_prompt, task_prompt=task_prompt, buffer=self.buffer)
            self.buffer.save_context(assistant={"content": assistant_response}, assistant_message_id=assistant_model.conversation_id)
            user_response = user_model.run(user_prompt=user_prompt, task_prompt=task_prompt, buffer=self.buffer)
            self.buffer.save_context(user={"content": user_response}, user_message_id=user_model.conversation_id)

        meta_response = self.meta_model.run(meta_prompt=meta_prompt, task_prompt=task_prompt, buffer=self.buffer)
        self.buffer.save_context(meta={"content": meta_response})

        return self.buffer
