from typing import (
    Tuple,
    List, 
    Dict,
    Any,
)

import numpy as np

from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

from langchain import LLMChain
from langchain.chat_models.base import BaseChatModel

from scai.memory.memory import ChatMemory

from scai.prompts.meta.models import MetaPrompt
from scai.memory.buffer import ConversationBuffer
from scai.prompts.task.models import TaskPrompt
from scai.prompts.metrics.models import MetricPrompt

from scai.agents.base import BaseAgent


class MetaPromptModel(BaseAgent):
    """LLM Chain for applying the meta-prompt agent."""
    def __init__(
        self, 
        llm: BaseChatModel, 
        model_id: str, 
    ) -> None:
        super().__init__(llm, model_id)

    def _get_collective_rating(
        self,
        chat_history: ChatMemory,
        metric_prompt: MetricPrompt,
    ) -> Dict[str, float]:
        """
        Returns the collective ratings. (eg for harmlessness)
        """
        collective_ratings = {}
        for model_id, responses in chat_history.items():
            _id, role = model_id.split("_")
            if _id not in collective_ratings:
                collective_ratings[_id] = []
            for response in responses:
                if role == 'user':
                    if len(response['responses_collective'].keys()) == self._get_n_user(chat_history) - 1:
                        collective_rating = {k: v for k, v in response['responses_collective'].items()}
                        collective_ratings[_id].append(collective_rating)
                    else:
                        collective_ratings[_id].append({metric_prompt.collective_metric: "0"})

        return collective_ratings
       
    def _get_chat_str(
        self,
        chat_history: ChatMemory,
        metric_prompt: MetricPrompt,
        task_prompt: TaskPrompt,
        max_tokens_assistant: int,
    ) -> str:
        """
        Formats the chat history into a string which is placed within the prompt.
        """
        # get collective ratings
        collective_ratings = self._get_collective_rating(chat_history, metric_prompt)
        # data structures for storing chat
        chat_dict = {}
        conversation_data = {}
        
        # get chat history string
        for model_id, responses in chat_history.items():
            _id, role = model_id.split("_")
            average_collective_ratings = []
            # initial message
            if _id not in chat_dict:
                prefix = '\n' if _id != '0' else ''
                chat_dict[_id] = [f"{prefix}Conversation {_id}:", f"user {_id} request: {task_prompt.preamble} '{task_prompt.task}' {task_prompt.assistant_connective.format(max_tokens=max_tokens_assistant)}"]
            if _id not in conversation_data:
                conversation_data[_id] = {'assistant': [], 'user': []}
            # loop over messages
            for response_idx, response in enumerate(responses):
                if role == 'user':
                    # compute average community metric for user
                    collective_metric = 0 
                    for k, v in collective_ratings.items():
                        if k != _id:
                            if len(v[response_idx]) == self._get_n_user(chat_history) - 1:
                                average_collective_ratings.append(float(int(v[response_idx][f"{_id}_assistant"])))
                    collective_metric  = np.mean(average_collective_ratings) if average_collective_ratings != [] else 0
                    average_collective_ratings = [] # reset
                    print(conversation_data, _id, role)
                    print(v)
                    conversation_data[_id][role].append(f"{role} {_id} feedback: {v['response']}\n{role} {_id} {metric_prompt.subjective_metric}: {v[metric_prompt.subjective_metric]}\nCollective {metric_prompt.collective_metric}: {collective_metric}")
                    v[f"{metric_prompt.collective_metric}_average"] = collective_metric
                elif role == 'assistant':
                    conversation_data[_id][role].append(f"{role} response: {response['response']}")
        # extend chatdict
        for _id, responses in conversation_data.items():
            for assistant, user in zip(responses['assistant'], responses['user']):
                chat_dict[_id].extend([assistant, user])

        return "\n".join("\n".join(value) for value in chat_dict.values())
    
    def _get_prompt(
        self,
        meta_prompt: MetaPrompt,
    ) -> ChatPromptTemplate:
        """
        Returns the prompt template for meta-prompt.
        """
        meta_promt_template = HumanMessagePromptTemplate.from_template(meta_prompt.content)
        if self.llm._llmrole == "CRFM": # crfm crashes without a system message at the beginning.
            system_prompt_template = SystemMessagePromptTemplate.from_template("Always respond to the best of your ability.\n")
            return ChatPromptTemplate.from_messages([system_prompt_template, meta_promt_template])
        return ChatPromptTemplate.from_messages([meta_promt_template])
    
    def _get_response(
        self,
        chat_prompt_template: ChatPromptTemplate,
        system_message_string: str,
        chat_history: ChatMemory,
        chat_history_string: str,
        max_tokens: int,
    ) -> str:
        """
        Returns the response from meta-prompt.
        """
        chain = LLMChain(llm=self.llm, prompt=chat_prompt_template)
        response = chain.run(system_history=system_message_string,
                             n_user=self._get_n_user(chat_history),
                             chat_history=chat_history_string,
                             max_tokens=max_tokens,
                             stop=['System:'])   
        response = self._format_response(response, ['Revision'])
        response['response'] = response.pop('Revision') # for consistency ('response' is the main output key)
        return response

    def run(
        self,
        buffer: ConversationBuffer,
        meta_prompt: MetaPrompt,
        task_prompt: TaskPrompt,
        metric_prompt: MetricPrompt,
        run: int,
        test_run: bool = False,
        verbose: bool = False,
        max_tokens_meta: int = 100,
        max_tokens_assistant: int = 100,
    ) -> str:
        """Runs meta-prompt

        Args:
            buffer (ConversationBuffer): Conversation buffer containing the chat history
            meta_prompt (MetaPrompt): Meta-prompt object containing the meta-prompt
            task_prompt (TaskPrompt): Task-prompt object containing the task-prompt
            turn (int): Turn number
            test_run (bool, optional): Whether to run in test mode. Defaults to False.
            verbose (bool, optional): Whether to print the prompt. Defaults to False.
            max_tokens_meta (int, optional): Maximum number of tokens for the meta-prompt. Defaults to 100.

        Returns:
            A dictionary containing the input prompt and meta-prompt responses (revised system message, etc)
        """
       
        
        # get previous constitution
        system_message = self._get_chat_history(buffer, memory_type='system')['system'][-1]['response']
        system_message_string = f"Constitution: {system_message}"
        
        # get chat history
        chat_history = self._get_chat_history(buffer, memory_type="chat")
        chat_history_string = self._get_chat_str(chat_history, metric_prompt, task_prompt, max_tokens_assistant)
        
        chat_prompt_template = self._get_prompt(meta_prompt)

        prompt_string = chat_prompt_template.format(system_history=system_message_string,
                                                    n_user=self._get_n_user(chat_history),
                                                    chat_history=chat_history_string,
                                                    max_tokens_assistant=max_tokens_assistant,
                                                    max_tokens=max_tokens_meta)
        if test_run:
            print('===================================')
            print(f'META {str(self.model_id)}')
            print(prompt_string)
            return {
                'response': f'constitution {run}', 
                'critique': 'meta-critique', 
                'system_message': 'system-message',
            }

        
        # response = self._get_response(chat_prompt_template, system_message, task_prompt, max_tokens_meta)

       
        # if verbose:
        #     print('===================================')
        #     print(f'META')
        #     print('Prompt: ', prompt)
        #     print('Response: ', response)

        # return response