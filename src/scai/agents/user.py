from typing import (
    Any,
    Dict,
    List, 
    Optional,
    Tuple,
)

from langchain.prompts.chat import (
    ChatPromptTemplate, 
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

from langchain.chains.llm import LLMChain
from langchain.chat_models.base import BaseChatModel

import numpy as np # for simulated responses

from scai.prompts.user.models import UserPrompt
from scai.prompts.task.models import TaskPrompt
from scai.prompts.metrics.models import MetricPrompt

from scai.memory.buffer import ConversationBuffer

from scai.agents.base import BaseAgent


class UserModel(BaseAgent):
    """LLM Chain for running the User."""
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
        metric_prompt: MetricPrompt,
    ) -> List[ChatPromptTemplate]:
        """
        Returns the chat history prompt templates for the user
        """
        chat_memory = self._get_chat_history(buffer, memory_type="chat") # check if chat memory exists
        assistant_response_0 = chat_memory[f"{self.model_id}_assistant"][-1]['response'] # get the initial assistant response
        # if we are at the beginning of a conversation
        if chat_memory.get(f"{self.model_id}_user") is None or len(chat_memory[f"{self.model_id}_user"]) == 0: 
            chat_history_prompt_templates = [
                HumanMessagePromptTemplate.from_template(
                    f"{task_prompt.preamble} '{task_prompt.content}' {task_prompt.user_connective} '{assistant_response_0}' \n{metric_prompt.content}"
                )
            ]
            return chat_history_prompt_templates
        # if we are not at the beginning of a conversation, need to get the conversation history
        chat_history_prompt_templates = [
            template
            for assistant, user in zip(chat_memory[f"{self.model_id}_assistant"], chat_memory[f"{self.model_id}_user"])
            for template in (AIMessagePromptTemplate.from_template(user['response']), 
                             HumanMessagePromptTemplate.from_template(assistant['response']))
        ]
        # add initial prompt including task
        chat_history_prompt_templates.insert(0, HumanMessagePromptTemplate.from_template(f"{task_prompt.preamble} {task_prompt.content} {task_prompt.user_connective} '{assistant_response_0}'"))
        # update final turn with metric request
        chat_history_prompt_templates[-1] = HumanMessagePromptTemplate.from_template(f"{chat_history_prompt_templates[-1].prompt.template}\n{metric_prompt.content}")
        return chat_history_prompt_templates
    
    def _get_chat_history_prompt_templates_other(
        self,
        buffer: ConversationBuffer,
        task_prompt: TaskPrompt,
        metric_prompt: MetricPrompt,
    ) -> Dict[str, ChatPromptTemplate]:
        """
        Returns the chat history prompt templates for the user rating other conversations
        """
        chat_memory = self._get_chat_history(buffer, memory_type="chat") # check if chat memory exists
        # data structures for storing the assistant responses and user responses from other conversations
        chat_history_prompt_templates_other = {}
        assistant_responses = {}
        user_responses = {}
        # if we are at the beginning of a conversation
        if chat_memory.get(f"{self.model_id}_user") is None or len(chat_memory[f"{self.model_id}_user"]) == 0: 
            for model_id in buffer.load_memory_variables(memory_type='chat').keys():
                if model_id != f"{self.model_id}_assistant" and 'assistant' in model_id:
                    assistant_responses[model_id] = chat_memory[model_id][-1]['response']
                    chat_history_prompt_templates = [
                        HumanMessagePromptTemplate.from_template(
                            f"{task_prompt.preamble} '{task_prompt.content}' {task_prompt.user_connective} '{assistant_responses[model_id]}' \n{metric_prompt.content_other}"
                        )
                    ]
                    chat_history_prompt_templates_other[model_id] = chat_history_prompt_templates
            return chat_history_prompt_templates_other
        # if we are not at the beginning of a conversation, need to get the conversation history
        for model_id in buffer.load_memory_variables(memory_type='chat').keys():
            if self.model_id not in model_id:
                if 'user' in model_id:
                    user_responses[model_id] = chat_memory[model_id][-1]['response']
                if 'assistant' in model_id:
                    assistant_responses[model_id] = chat_memory[model_id][-1]['response']
                chat_history_prompt_templates = [
                        template
                        for assistant, user in zip(chat_memory[model_id], chat_memory[model_id])
                        for template in (AIMessagePromptTemplate.from_template(assistant['response']), 
                                         HumanMessagePromptTemplate.from_template(user['response']))
                    ]
                # insert the initial request at the beginning of the chat history
                chat_history_prompt_templates.insert(0, HumanMessagePromptTemplate.from_template(f"{task_prompt.preamble} '{task_prompt.content}' {task_prompt.assistant_connective}")) # insert task prompt at the beginning
                # create a request for the next response
                chat_history_prompt_templates[-1] = HumanMessagePromptTemplate.from_template(f"{chat_history_prompt_templates[-1].prompt.template}\n{metric_prompt.content_other}")
                # add to dictionary
                chat_history_prompt_templates_other[model_id] = chat_history_prompt_templates
        return chat_history_prompt_templates_other

    def _get_prompt(
        self, 
        buffer: ConversationBuffer,
        user_prompt: UserPrompt,
        task_prompt: TaskPrompt,
        metric_prompt: MetricPrompt,
    ) -> ChatPromptTemplate:
        """
        Get prompt for user.
        """
        system_prompt_template = SystemMessagePromptTemplate.from_template(user_prompt.content)
        chat_history_prompt_templates = self._get_chat_history_prompt_templates(buffer, task_prompt, metric_prompt)
        return ChatPromptTemplate.from_messages([system_prompt_template, *chat_history_prompt_templates])
    
    def _get_prompt_other(
        self, 
        buffer: ConversationBuffer,
        user_prompt: UserPrompt,
        task_prompt: TaskPrompt,
        metric_prompt: MetricPrompt,
    ) -> Dict[str, ChatPromptTemplate]:
        """
        Get prompt for user.
        """
        system_prompt_template = SystemMessagePromptTemplate.from_template(user_prompt.content)
        chat_history_prompt_templates_other = self._get_chat_history_prompt_templates_other(buffer, task_prompt, metric_prompt)
        chat_prompt_templates_other = {model_id:
                ChatPromptTemplate.from_messages([system_prompt_template, *chat_history_prompt_template_other])
                for model_id, chat_history_prompt_template_other in chat_history_prompt_templates_other.items()
            }
        return chat_prompt_templates_other
    
    def _get_response(
        self,
        chat_prompt_template: ChatPromptTemplate,
        system_message: str,
        task_prompt: TaskPrompt,
        metric_prompt: MetricPrompt,
        max_tokens: int,
    ) -> str:
        """
        Returns the response from the assistant.
        """
        chain = LLMChain(llm=self.llm, prompt=chat_prompt_template)
        response = chain.run(system_message=system_message,
                             task=task_prompt.content,
                             max_tokens=max_tokens,
                             stop=['System:'])  
        response = self._format_response(response, metric_prompt.metrics)
        response['response'] = response.pop('Feedback') # feedback is actual `response` fed into next turn
        return response
    
    def _get_response_other(
        self,
        chat_prompt_templates: Dict[str, ChatPromptTemplate],
        system_message: str,
        task_prompt: TaskPrompt,
        metric_prompt: MetricPrompt,
        max_tokens: int,
    ) -> Dict[str, Any]:
        """
        Gets response for other users.
        """
        responses_other = {}
        for model_id, chat_prompt_template in enumerate(chat_prompt_templates):
            chain = LLMChain(llm=self.llm, prompt=chat_prompt_template) 
            response = chain.run(system_message=system_message,
                                 task=task_prompt.content,
                                 max_tokens=max_tokens,
                                 stop=['System:'])
            response = self._format_response(response, metric_prompt.metrics_other)
            response['response'] = response.pop('Feedback') # feedback is actual `response` fed into next turn
            responses_other[model_id] = response

        return responses_other
    
    def run(
        self,
        buffer: ConversationBuffer,
        user_prompt: UserPrompt,
        task_prompt: TaskPrompt,
        metric_prompt: MetricPrompt,
        turn: int,
        test_run: bool = True,
        verbose: bool = False,
        max_tokens: int = 100,
    ) -> Dict[str, Any]:
        """Runs the user.

        Args:
            buffer (ConversationBuffer): Conversation buffer containing the chat history
            user_prompt (UserPrompt): User prompt containing the user's response
            task_prompt (TaskPrompt): Task prompt containing the task
            metric_prompt (MetricPrompt): Metric prompt containing the metrics
            turn (int): Turn number
            test_run (bool, optional): Whether this is a test run. Defaults to True.
            verbose (bool, optional): Whether to print the chat history. Defaults to False.
            max_tokens (int, optional): Maximum number of tokens to generate. Defaults to 100.

        Returns:
            A dictionary containing the user's response, input prompt, and all other metrics we want to track.
        """
        system_message = user_prompt.persona
        chat_prompt_template = self._get_prompt(buffer, user_prompt, task_prompt, metric_prompt)
        chat_prompt_templates_other = self._get_prompt_other(buffer, user_prompt, task_prompt, metric_prompt)
        prompt_string = chat_prompt_template.format(system_message=system_message, 
                                                    task=task_prompt.task,
                                                    metric_prompt=metric_prompt.content,
                                                    max_tokens=max_tokens)
        prompt_strings_other = {model_id: chat_prompt_template_other.format(system_message=system_message,
                                                                  task=task_prompt.task,
                                                                  metric_prompt=metric_prompt.content,
                                                                  max_tokens=max_tokens)
                                for model_id, chat_prompt_template_other in chat_prompt_templates_other.items()
            }
        if test_run:
            print('===================================')
            print(f'USER {str(self.model_id)} turn {turn}')
            print(prompt_string)
            print(prompt_strings_other)

            return {
                'prompt': prompt_string, 
                'prompts_other': prompt_strings_other,
                'response': f"user_response_{self.model_id}, turn {turn}.",
                'responses_other': {model_id: f"user_response_{model_id}, turn {turn}." for model_id in chat_prompt_templates_other.keys()},
                'turn': turn
            }

        response = self._get_response(chat_prompt_template, system_message, task_prompt, metric_prompt, max_tokens)
        responses_other = self._get_response_other(chat_prompt_templates_other, system_message, task_prompt, metric_prompt, max_tokens)

        if verbose:
            print('===================================')
            print(f'USER {str(self.model_id)} turn {turn}')
            print(response)
            print(responses_other)

        return {
            'prompt': prompt_string, 
            'prompts_other': prompt_strings_other,
            'full_response': response, 
            'response': response['response'],
            'responses_other': responses_other,
            'turn': turn
        }