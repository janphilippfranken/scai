from typing import (
    Any,
    Dict,
    List, 
    Optional,
    Tuple
)

from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

from langchain.chains.llm import LLMChain
from langchain.chat_models.base import BaseChatModel

from scai.prompts.assistant.models import AssistantPrompt
from scai.prompts.task.models import TaskPrompt

from scai.memory.buffer import ConversationBuffer

from scai.agents.base import BaseAgent

class AssistantAgent(BaseAgent):
    """Assistant agent."""
    def __init__(
        self, 
        llm: BaseChatModel, 
        model_id: str, 
    ) -> None:
        super().__init__(llm, model_id)

    def _get_chat_history_prompt_templates(
        self,
        buffer: ConversationBuffer,
        task_prompt: TaskPrompt,
    ) -> List[ChatPromptTemplate]:
        """
        Returns the chat history prompt templates for the assistant.
        """
        chat_memory = self._get_chat_history(buffer, memory_type="chat") # check if chat memory exists
        if chat_memory.get(f"{self.model_id}_assistant") is None or len(chat_memory[f"{self.model_id}_assistant"] == 0): # if we are at the beginning of a conversation
            chat_history_prompt_templates = [
                HumanMessagePromptTemplate.from_template(
                    f"{task_prompt.preamble} '{task_prompt.content}' {task_prompt.assistant_connective}"
                )
            ]
            return chat_history_prompt_templates
        # if a chat history exists 
        chat_history_prompt_templates = [
                response
                for assistant, user in zip(chat_memory[f"assistant_{self.model_id}"], chat_memory[f"user_{self.model_id}"])
                for response in (AIMessagePromptTemplate.from_template(assistant['response']), 
                                 HumanMessagePromptTemplate.from_template(user['response']))
            ]
        # insert the initial request at the beginning of the chat history
        chat_history_prompt_templates.insert(0, HumanMessagePromptTemplate.from_template(f"{task_prompt.preamble} '{task_prompt.content}' {task_prompt.assistant_connective}")) # insert task prompt at the beginning
        # create a request for the next response
        chat_history_prompt_templates[-1] = HumanMessagePromptTemplate.from_template(chat_history_prompt_templates[-1].prompt.template)
        return chat_history_prompt_templates
       
    def _get_prompt(
        self,
        buffer: ConversationBuffer,
        assistant_prompt: AssistantPrompt,
        task_prompt: TaskPrompt,
    ) -> ChatPromptTemplate:
        """
        Returns the prompt template for the assistant.
        """
        system_prompt_template = SystemMessagePromptTemplate.from_template(f"{assistant_prompt.content}\n")
        chat_history_prompt_templates = self._get_chat_history_prompt_templates(buffer, task_prompt)
        return ChatPromptTemplate.from_messages([system_prompt_template, *chat_history_prompt_templates])
       
    def _get_response(
        self,
        chat_prompt_template: ChatPromptTemplate,
        system_message: str,
        task_prompt: TaskPrompt,
        max_tokens: int,
    ) -> str:
        """
        Returns the response from the assistant.
        """
        chain = LLMChain(llm=self.llm, prompt=chat_prompt_template)
        response = chain.run(system_message=system_message,
                             task=task_prompt.task,
                             max_tokens=max_tokens,
                             stop=['System:'])   
        return response

    def run(
        self, 
        buffer: ConversationBuffer, 
        assistant_prompt: AssistantPrompt, 
        task_prompt: TaskPrompt, 
        turn: int,
        test_run: bool = False, 
        verbose: bool = False,
        max_tokens: int = 100,
    ) -> Dict[str, Any]:
        """Runs the assistant

        Args:
            buffer: The buffer containing the conversation history.
            assistant_prompt: The assistant prompt to be used.
            task_prompt: The task prompt to be used.
            turn: The turn number.
            metric_prompt: The metric prompt to be used.
            test_run: Whether to run the assistant in test mode (i.e., without using tokens, just print prompt and save simulated response).
            verbose: Whether to print the prompt and response.
            max_tokens: The maximum number of tokens to generate.

        Returns:
            A dictionary containing the assistant's response, input prompt, and all other metrics we want to track.
        """
        system_message = self._get_chat_history(buffer, memory_type="system")['system'][-1]['response'] # the last system message in the chat history (i.e. constitution)
        chat_prompt_template= self._get_prompt(buffer, assistant_prompt, task_prompt)
        prompt_string = chat_prompt_template.format(system_message=system_message,
                                                    task=task_prompt.task,
                                                    max_tokens=max_tokens)
        if test_run:
            print('===================================')
            print(f'ASSISTANT {str(self.model_id)}')
            print(prompt_string)

            return {
                'prompt': prompt_string, 
                'response': f"assistant_response_{self.model_id}, turn {turn}.",
                'turn': turn
            }
        breakpoint()
        
        response = self._get_response(chat_prompt_template, system_message, task_prompt, max_tokens)

        if verbose:
            print('===================================') 
            print(f"ASSISTANT {str(self.model)}")
            print(f"prompt:{prompt_string}")
            print(f"response: {response}")

        return {
            'prompt': prompt_string, 
            'response': response, 
            'turn': turn
        }