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

from langchain.chains.llm import LLMChain
from langchain.chat_models.base import BaseChatModel

from scai.assistant.models import AssistantPrompt
from scai.assistant.prompts import ASSISTANT_PROMPTS
from scai.memory.buffer import ConversationBuffer
from scai.task.models import TaskPrompt


class AssistantModel():
    """LLM Chain for applying the AI Assitant."""
    def __init__(
        self, 
        llm: BaseChatModel, 
        conversation_id: str, 
        k: int = 5, 
        system_k: int = 5,
    ) -> None:
        """Initializes the AssistantModel with a given LLM and conversation id.

        Args:
            llm: The LLM Chat model. Currently either a CRFM or OpenAI model chat model
            conversation_id: The unique identifier for the conversation.
            k: The assistant's chat memory length (i.e. how many previous turns do we feed to the user model)
            system_k: The number of past system messages visible to the meta-prompt agent
        """
        self.llm = llm
        self.conversation_id = conversation_id
        self.k = k
        self.system_k = system_k

    def _get_chat_history(
        self, 
        buffer: ConversationBuffer, 
        var_type: str,
    ) -> List[str]:
        """
        Gets chat history from buffer.
        """
        assert var_type in ["system", "user", "assistant"], f"var_type must be 'system', 'user', 'assistant', got {var_type}"
        if var_type == "system":
            return buffer.load_memory_variables(var_type=var_type)[var_type][-self.system_k:] if self.system_k > 0 else []
        elif var_type in ["user", "assistant"]:
            return buffer.load_memory_variables(var_type='chat').get(f"{self.conversation_id}_{var_type}", [])[-self.k:] if self.k > 0 else []

    def run(
        self, 
        buffer: ConversationBuffer, 
        assistant_prompt: AssistantPrompt, 
        task_prompt: TaskPrompt, 
        test_run: bool = False, 
        verbose: bool = False,
        max_tokens: int = 100,
    ) -> Dict[str, Any]:
        """Runs the assistant

        Args:
            buffer: The buffer containing the conversation history.
            assistant_prompt: The assistant prompt to be used.
            task_prompt: The task prompt to be used.
            metric_prompt: The metric prompt to be used.
            test_run: Whether to run the assistant in test mode (i.e., without using tokens, just print prompt and save simulated response).
            verbose: Whether to print the prompt and response.
            max_tokens: The maximum number of tokens to generate.

        Returns:
            A dictionary containing the input prompt and the assistant's responses.
        """
        assistant_system_prompt = SystemMessagePromptTemplate.from_template(assistant_prompt.content)
        chat_data = buffer.load_memory_variables(var_type='chat') # check if chat data exists

        if chat_data and len(self._get_chat_history(buffer, var_type="assistant")) > 0: # if we are not at the first and the assistant's chat memory is not 0
            assistant_chat_history = self._get_chat_history(buffer, var_type="assistant")
            user_chat_history = self._get_chat_history(buffer, var_type="user")
            chat_history_prompts = [
                response
                for assistant, user in zip(assistant_chat_history, user_chat_history)
                for response in (AIMessagePromptTemplate.from_template(assistant['response']), 
                                HumanMessagePromptTemplate.from_template(user['response']))
            ]
            chat_history_prompts.insert(0, HumanMessagePromptTemplate.from_template(task_prompt.content)) # insert task prompt at the beginning
            chat_history_prompts[-1] = HumanMessagePromptTemplate.from_template(chat_history_prompts[-1].prompt.template + task_prompt.assistant_connective)
        else:
            chat_history_prompts = [HumanMessagePromptTemplate.from_template(task_prompt.preamble + " '" + task_prompt.content + "' " + task_prompt.assistant_connective)]
        
        assistant_chat_prompt = ChatPromptTemplate.from_messages([assistant_system_prompt, *chat_history_prompts])
        system_message = self._get_chat_history(buffer, var_type="system")[-1]['response']

        prompt = assistant_chat_prompt.format(system_message=system_message,
                                              task=task_prompt.task,
                                              max_tokens=max_tokens)
        # if verbose, just print the prompt and return
        if test_run:
            print('===================================')
            print(f'ASSISTANT {str(self.conversation_id)}')
            print(prompt)
            return {

                'prompt': prompt,
                'response': "assistant_response_" + str(self.conversation_id) + "."
            }

        chain = LLMChain(llm=self.llm, prompt=assistant_chat_prompt)
        response = chain.run(system_message=system_message,
                             task=task_prompt.task,
                             max_tokens=max_tokens,
                             stop=['System:'])    
        
        if verbose:
            print('===================================')
            print(f'ASSISTANT {str(self.conversation_id)}')
            print('Prompt: ', prompt)
            print('Response: ', response)

        return {'prompt': prompt, 'response': response}
    