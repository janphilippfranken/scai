"""The Assistant."""
from typing import (
    Any,
    Dict,
    List, 
    Optional
)

from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

from langchain.schema import (
    AIMessage,
    BaseMessage,
    ChatMessage,
    HumanMessage,
    SystemMessage,
)

from scai.modules.assistant.models import AssistantPrompt
from scai.modules.assistant.prompts import ASSISTANT_PROMPTS
from scai.modules.memory.buffer import CustomConversationBufferWindowMemory

from scai.modules.task.models import TaskPrompt

from langchain.chains.llm import LLMChain

class AssistantModel():
    """Chain for applying the AI Assitant.

    Example:
        .. code-block:: python

            

    """

    def __init__(self, llm, conversation_id) -> None:
        self.llm = llm
        self.conversation_id = conversation_id
    
    def _convert_message_to_dict(self, message: BaseMessage) -> dict:
        if isinstance(message, ChatMessage):
            message_dict = {"role": message.role, "content": message.content}
        elif isinstance(message, HumanMessage):
            message_dict = {"role": "user", "content": message.content}
        elif isinstance(message, AIMessage):
            message_dict = {"role": "assistant", "content": message.content}
        elif isinstance(message, SystemMessage):
            message_dict = {"role": "system", "content": message.content}
        else:
            raise ValueError(f"Got unknown type {message}")
        if "name" in message.additional_kwargs:
            message_dict["name"] = message.additional_kwargs["name"]
        return message_dict

    def run(
        self,
        buffer: CustomConversationBufferWindowMemory,
        assistant_prompt: AssistantPrompt,
        task_prompt: TaskPrompt,
        verbose: bool = False,
    ) -> str:
        """Run assistant."""
        assistant_system_prompt = SystemMessagePromptTemplate.from_template(assistant_prompt.content)
        # get chat history for the specific conversation
        chat_history_prompts = [
            message
            for message, message_id in zip(
                buffer.load_memory_variables(var_type="assistant")["history"],
                buffer.chat_memory.message_ids
            )
            if self.conversation_id in message_id
        ]
        # get system history
        system_history_prompts = [m for m in buffer.load_memory_variables(var_type="system", use_assistant_system_k = True)['history']]
        # prompt to generate next completion based on history
        generate_next = """Respond within {max_tokens} tokens, using prior user messages as feedback for revision."""
        generate_next_prompt = HumanMessagePromptTemplate.from_template(generate_next)
        # build prompt template
        assistant_chat_prompt = ChatPromptTemplate.from_messages([assistant_system_prompt, *chat_history_prompts, generate_next_prompt])
        # full prompt fed into the model
        prompt = assistant_chat_prompt.format(system_message=system_history_prompts[-1].content, # for now just take content of latest system message
                                              task=task_prompt.content,
                                              max_tokens=assistant_prompt.max_tokens)
        # if verbose we just print the prompt and return it
        if verbose:
            print()
            print(f'ASSISTANT {str(self.conversation_id)}')
            print(prompt)
            print()
            return {'Prompt': prompt,'Response': "assistant_response_" + str(self.conversation_id)}
       
        # build chain
        chain = LLMChain(llm=self.llm, prompt=assistant_chat_prompt)
        # run chain
        response = chain.run(system_message=system_history_prompts[-1].content, # for now just take content of latest system message
                             task=task_prompt.content,
                             max_tokens=assistant_prompt.max_tokens, 
                             stop=['System:'])
        
        return {'Prompt': prompt,'Response': response}
        