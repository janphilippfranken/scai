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

from langchain.chains.llm import LLMChain

from scai.assistant.models import AssistantPrompt
from scai.assistant.prompts import ASSISTANT_PROMPTS
from scai.memory.buffer import ConversationBuffer
from scai.task.models import TaskPrompt


class AssistantModel():
    """LLM Chain for applying the AI Assitant."""

    def __init__(self, llm, conversation_id: str, k: int = 5, system_k: int = 5) -> None:
        self.llm = llm
        self.conversation_id = conversation_id
        self.k = k
        self.system_k = system_k

    def _get_chat_history(self, buffer: ConversationBuffer, var_type: str) -> List[str]:
        assert var_type in ["system", "user", "assistant"], f"var_type must be 'system', 'user', 'assistant', got {var_type}"
        if var_type == "system":
            return buffer.load_memory_variables(var_type=var_type)[var_type][-self.system_k:] if self.system_k > 0 else []
        elif var_type in ["user", "assistant"]:
            return buffer.load_memory_variables(var_type='chat').get(f"{self.conversation_id}_{var_type}", [])[-self.k:] if self.k > 0 else []

    def run(self, buffer: ConversationBuffer, assistant_prompt: AssistantPrompt, task_prompt: TaskPrompt, test_run: bool = False, verbose: bool = False) -> str:
        assistant_system_prompt = SystemMessagePromptTemplate.from_template(assistant_prompt.content)
        
        chat_data = buffer.load_memory_variables(var_type='chat') # check iff chat data exists
        if chat_data and len(self._get_chat_history(buffer, var_type="assistant")) > 0:
            assistant_chat_history = self._get_chat_history(buffer, var_type="assistant")
            user_chat_history = self._get_chat_history(buffer, var_type="user")
            
            chat_history_prompts = [
                response
                for assistant, user in zip(assistant_chat_history, user_chat_history)
                for response in (AIMessagePromptTemplate.from_template(assistant['response']), 
                                HumanMessagePromptTemplate.from_template(user['response']))
            ]
            chat_history_prompts.insert(0, HumanMessagePromptTemplate.from_template(task_prompt.content))
            chat_history_prompts[-1] = HumanMessagePromptTemplate.from_template(chat_history_prompts[-1].prompt.template + " Revise your response within {max_tokens} tokens.")
        else:
            chat_history_prompts = [HumanMessagePromptTemplate.from_template(task_prompt.content + " Respond within {max_tokens} tokens.")]
        
        assistant_chat_prompt = ChatPromptTemplate.from_messages([assistant_system_prompt, *chat_history_prompts])
        system_message = self._get_chat_history(buffer, var_type="system")[-1]['response']

        prompt = assistant_chat_prompt.format(system_message=system_message,
                                              task=task_prompt.task,
                                              max_tokens=assistant_prompt.max_tokens)
        # if verbose, just print the prompt and return
        if test_run:
            print()
            print(f'ASSISTANT {str(self.conversation_id)}')
            print(prompt)
            print()
            return {'prompt': prompt,'response': "assistant_response_" + str(self.conversation_id) + "."}

        chain = LLMChain(llm=self.llm, prompt=assistant_chat_prompt)
        response = chain.run(system_message=system_message,
                             task=task_prompt.task,
                             max_tokens=assistant_prompt.max_tokens, 
                             stop=['System:'])
        if verbose:
            print()
            print("-----------------------------------")
            print("ASSISTANT PROMPT")
            print(prompt)
            print("ASSISTANT RESPONSE")
            print(response)
            print("-----------------------------------")
        return {'prompt': prompt,'response': response}
    