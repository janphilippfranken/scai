from typing import Dict

import numpy as np
import copy

from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
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
    """
    LLM Chain for running the meta-prompt agent.
    """
    def __init__(
        self, 
        llm: BaseChatModel, 
        model_id: str, 
    ) -> None:
        super().__init__(llm, model_id)

    def _get_collective_rating(
        self,
        chat_history: ChatMemory,
    ) -> Dict[str, float]:
        """
        Returns the collective ratings provided by each user for the other user conversations (eg for harmlessness).

        Args:
            chat_history: (ChatMemory) The chat history.

        Returns:
            Dict of collective ratings.
        """
        collective_ratings = {}
        for model_id, responses in chat_history.items():
            _id, role = model_id.split("_")
            if _id not in collective_ratings:
                collective_ratings[_id] = []
            for response in responses:
                if role == 'user':
                    collective_rating = {k: v for k, v in response['responses_collective'].items() if 'assistant' in k}
                    collective_ratings[_id].append(collective_rating) # TODO: Fix this for the first user
        return collective_ratings
       
    def _get_chat_str(
        self,
        chat_history: ChatMemory,
        metric_prompt: MetricPrompt,
        task_prompt: TaskPrompt,
        max_tokens_assistant: int,
    ) -> str:
        """
        Formats the chat history into a string which is placed within the meta-prompt prompt.

        Args:
            chat_history: (ChatMemory) The chat history.
            metric_prompt: (MetricPrompt) The metric prompt.
            task_prompt: (TaskPrompt) The task prompt.
            max_tokens_assistant: (int) The maximum number of tokens for the assistant.

        Returns:
            The chat history string.
        """
        # get collective ratings
        collective_ratings = self._get_collective_rating(chat_history)
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
                chat_dict[_id] = [f"{prefix}Conversation {_id}:", f"user {_id} request: {task_prompt.preamble} {task_prompt.task} {task_prompt.assistant_connective.format(max_tokens=max_tokens_assistant)}"]
            if _id not in conversation_data:
                conversation_data[_id] = {'assistant': [], 'user': []}
            # loop over messages
            for response_idx, response in enumerate(responses):
                if role == 'user':
                    # compute average collective metric for users
                    collective_metric = 0 
                    for k, v in collective_ratings.items():
                        # if v[0] == {}:
                        #     v[0] = copy.deepcopy(v[1]) # for now just duplicate the second rating for user 0
                        if k != _id:
                            if len(v[response_idx]) == self._get_n_user(chat_history) - 1:
                                average_collective_ratings.append(float(v[response_idx][f"{_id}_assistant"][metric_prompt.collective_metric.capitalize()]))
                    collective_metric  = np.mean(average_collective_ratings)/10 if average_collective_ratings != [] else 0
                    if collective_metric == 0:
                        collective_metric = 50 # if no ratings, assume 5 for now
                    average_collective_ratings = [] # reset
                    conversation_data[_id][role].append(f"{role} {_id} feedback: {response['response']}") # add these to include metrics \n{role} {_id} {metric_prompt.subjective_metric} rating: {response[metric_prompt.subjective_metric]}\ncollective {metric_prompt.collective_metric} rating: {collective_metric}")
                    response[f"{metric_prompt.collective_metric}_average"] = collective_metric # store average metric
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

        Args:
            meta_prompt: (MetaPrompt) The meta-prompt.

        Returns:
            The prompt template.
        """
        meta_prompt_template = HumanMessagePromptTemplate.from_template(meta_prompt.content)
        if self.llm._llm_type == "CRFM": # crfm crashes without a system message at the beginning.
            system_prompt_template = SystemMessagePromptTemplate.from_template("Always respond to the best of your ability.\n")
            return ChatPromptTemplate.from_messages([system_prompt_template, meta_prompt_template])
        return ChatPromptTemplate.from_messages([meta_prompt_template])
    
    def _get_response(
        self,
        chat_prompt_template: ChatPromptTemplate,
        developer_constitution: str,
        social_contract: str,
        chat_history: ChatMemory,
        chat_history_string: str,
        max_tokens_assistant: int,
        max_tokens_meta: int,
        metric_prompt: MetricPrompt,
        meta_prompt: MetaPrompt,
    ) -> str:
        """
        Returns the response from meta-prompt.

        Args:   
            chat_prompt_template: (ChatPromptTemplate) The chat prompt template.
            developer_constitution: (str) The developer constitution.
            social_contract: (str) The social contract.
            chat_history: (ChatMemory) The chat history.

        Returns:
            The response from meta-prompt.
        """
        chain = LLMChain(llm=self.llm, prompt=chat_prompt_template)
        response = chain.run(developer_constitution=developer_constitution,
                             social_contract=social_contract,
                             n_user=self._get_n_user(chat_history),
                             chat_history=chat_history_string,
                             max_tokens_assistant=max_tokens_assistant,
                             max_tokens_revision=max_tokens_meta//2,
                             subjective_metric=metric_prompt.subjective_metric,
                             collective_metric=metric_prompt.collective_metric,
                             stop=['System:'])   
        response = self._format_response(response, meta_prompt.metrics)
        response['response'] = f"{response[meta_prompt.metrics[0]]} Learned USER PREFERENCES: {response[meta_prompt.metrics[1]]}"
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
            buffer (ConversationBuffer): The conversation buffer
            meta_prompt (MetaPrompt): The meta-prompt
            task_prompt (TaskPrompt): The task prompt
            metric_prompt (MetricPrompt): The metric prompt
            run (int): The run number
            test_run (bool, optional): Whether this is a test run. Defaults to False.
            verbose (bool, optional): Whether to print the meta-prompt. Defaults to False.
            max_tokens_meta (int, optional): The maximum number of tokens for the meta-prompt. Defaults to 100.
            max_tokens_assistant (int, optional): The maximum number of tokens for the assistant. Defaults to 100.

        Returns:
            A dictionary containing the input prompt and meta-prompt responses (revised system message, etc)
        """
        # get previous system messages (i.e. developer constitution and social contract)
        developer_constitution_string = self._get_chat_history(buffer, memory_type='system')['system'][-1]['full_response'][meta_prompt.metrics[0]]
        social_contract_string = self._get_chat_history(buffer, memory_type='system')['system'][-1]['full_response'][meta_prompt.metrics[1]]
        # get chat history
        chat_history = self._get_chat_history(buffer, memory_type="chat")
        chat_history_string = self._get_chat_str(chat_history, metric_prompt, task_prompt, max_tokens_assistant)
        # get meta-prompt template and string
        chat_prompt_template = self._get_prompt(meta_prompt)
        prompt_string = chat_prompt_template.format(developer_constitution=developer_constitution_string,
                                                    social_contract=social_contract_string,
                                                    n_user=self._get_n_user(chat_history),
                                                    chat_history=chat_history_string,
                                                    max_tokens_assistant=max_tokens_assistant,
                                                    max_tokens_revision=max_tokens_meta,
                                                    subjective_metric=metric_prompt.subjective_metric,
                                                    collective_metric=metric_prompt.collective_metric)

        response = self._get_response(chat_prompt_template, 
                                      developer_constitution_string,
                                      social_contract_string,
                                      chat_history,
                                      chat_history_string,
                                      max_tokens_assistant,
                                      max_tokens_meta,
                                      metric_prompt,
                                      meta_prompt)
        
        if verbose:
            print('===================================')
            print(f'META {str(self.model_id)}')
            print('prompt')
            print(prompt_string)
            # print('response')
            # print(response['response'])
            # print('full response')
            # print(response)
            # print('run', run)
        
        return {
                'prompt': prompt_string,
                'response': response['response'],
                'full_response': response,
                'run': run,
            }