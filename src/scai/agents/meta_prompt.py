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

from scai.prompts.meta_prompt.models import MetaPrompt
from scai.memory.buffer import ConversationBuffer
from scai.prompts.task.models import TaskPrompt
from scai.prompts.metrics.models import MetricPrompt


# TODO: add to base class
def get_vars_from_out(out: str, var_list: list) -> dict[str, str]:
    var_dict = {}
    for lines in out.splitlines():
        for var in var_list:
            if f'{var}:' in lines:
                var_dict[var] = lines.split(': ')[1].strip()
    return var_dict

class MetaPromptModel():
    """LLM Chain for applying the meta-prompt agent."""
    def __init__(
        self, 
        llm: BaseChatModel,
        model_id: str,
        k: int = 5,
    ) -> None:
        """Initializes the MetaPromptModel with a given LLM and conversation id.
        Args:
            llm: The LLM Chat model. Currently either a CRFM or OpenAI model chat model
            model_id: The unique identifier for the conversation.
            k: Meta-prompt chat memory length (i.e. how many previous turns do we feed to the model)
        """
        self.llm = llm
        self.model_id = model_id
        self.k = k
    
    def _get_chat_str(
        self,
        chat_history: Dict[str, List[Any]],
        task_prompt: TaskPrompt,
        max_tokens_assistant: int,
    ) -> str:
        """
        Formats the chat history into a string which is placed within the prompt.
        -----------------------
        """
        chat_dict = {}
        conversation_data = {}


        # get harmlessness ratings
        harmlessness_ratings = {}
        for key, value in chat_history.items():
            id, role = key.split("_")
            if id not in harmlessness_ratings:
                harmlessness_ratings[id] = []
            for v in value:
                if role == 'user':
                    if len(v['responses_other'].keys()) == self._get_n_user(chat_history) - 1:
                        harmlessness = {k_other: v_other['harmlessness'] for k_other, v_other in v['responses_other'].items()}
                        harmlessness_ratings[id].append(harmlessness)
                    else:
                        harmlessness_ratings[id].append({'harmlessness': "0"})

        # get chat history
        for key, value in chat_history.items():
            id, role = key.split("_")
            average_harmlessness = []
            # initial message
            if id not in chat_dict:  
                prefix = "\n" if id != '0' else ""
                chat_dict[id] = [f"{prefix}Conversation {id}:", f"user {id} request: {task_prompt.preamble} '{task_prompt.task}' {task_prompt.assistant_connective.format(max_tokens=max_tokens_assistant)}"]
            if id not in conversation_data:
                conversation_data[id] = {'assistant': [], 'user': []}
            
            # loop over messages
            for idx, v in enumerate(value):
                if role == 'user':

                    # compute average harmlessness if available
                    harmlessness = 0 # TODO: make sure we dont hardcode harmlessness
                    for k_harmless, v_harmless in harmlessness_ratings.items():
                        if k_harmless != id:
                            if len(v_harmless[idx]) == self._get_n_user(chat_history) - 1:
                                average_harmlessness.append(float(int(v_harmless[idx][f"{id}_assistant"])))
                    harmlessness = np.mean(average_harmlessness) if average_harmlessness != [] else 0
                    average_harmlessness = [] # reset
                    conversation_data[id][role].append(f"{role} {id} feedback: {v['response']}\n{role} {id} satisfaction: {v['Satisfaction']}\ncollective harmlessness: {harmlessness}")
                    v['harmlessness_other'] = harmlessness
                elif role == 'assistant':
                    conversation_data[id][role].append(f"{role} response: {v['response']}")

        for id, data in conversation_data.items():
            for assistant, user in zip(data['assistant'], data['user']):
                chat_dict[id].extend([assistant, user])
        

        return "\n".join("\n".join(value) for value in chat_dict.values())

    def run(
        self,
        buffer: ConversationBuffer,
        meta_prompt: MetaPrompt,
        task_prompt: TaskPrompt,
        test_run: bool = False,
        verbose: bool = False,
        max_tokens: int = 100,
        max_tokens_assistant: int = 100,
    ) -> str:
        """Runs meta-prompt

        Args:
            buffer: The buffer containing the conversation history.
            meta_prompt: The meta prompt to be used.
            task_prompt: The task prompt to be used.
            test_run: Whether to run meta-prompt in test mode (i.e., without using tokens, just print prompt and save simulated response).
            verbose: Whether to print the prompt and response.
            max_tokens: The maximum number of tokens to use for the meta-prompt.
            max_tokens_assistant: The maximum number of tokens to use for the assistant.

        Returns:
            A dictionary containing the input prompt, critique response, and meta-prompt response (i.e. revised system message)
        """
        if self.llm._llm_type == "CRFM": # TODO: crfm crashes without a system messages, need to check if we can fix this
            meta_start_prompt_template = SystemMessagePromptTemplate.from_template("Please be as helpful as possible.") 
        meta_prompt_template = HumanMessagePromptTemplate.from_template(meta_prompt.content)
        # past constiutions
        system_messages = self._get_chat_history(buffer, memory_type='system')
        system_message_string = "\n".join(f"Constitution: {system['response']}" for system in system_messages).rstrip('\n')
        # chat history
        chat_history = buffer.load_memory_variables(memory_type='chat')
        chat_history_string = self._get_chat_str(chat_history=chat_history, task_prompt=task_prompt, max_tokens_assistant=max_tokens_assistant)
        # build prompt
        meta_chat_prompt = ChatPromptTemplate.from_messages([meta_start_prompt_template, meta_prompt_template])
        # format for verbose/test_run
        prompt = meta_chat_prompt.format(n_user=self._get_n_user(chat_history),
                                         chat_history=chat_history_string,
                                         system_history=system_message_string,
                                         max_tokens_critique=max_tokens//2,
                                         max_tokens_revision=max_tokens//2)
        # if test_run we just print the prompt and return the type of response we would get
        if test_run:
            print('===================================')
            print(f'META')
            print(prompt)
            print('===================================')
            return {'response': 'system', 
                'critique': 'meta-critique', 
                'system_message': 'system-message',
            }
        # run chain
        chain = LLMChain(llm=self.llm, prompt=meta_chat_prompt)
        response = chain.run(n_user=self._get_n_user(chat_history),
                            chat_history=chat_history_string,
                            system_history=system_message_string,
                            max_tokens_critique=max_tokens//2,
                            max_tokens_revision=max_tokens//2,
                            stop=['System:'])
        # get variables from output
        response = get_vars_from_out(response, ['Critique', 'Revision'])
        response['response'] = response.pop('Revision') # for consistency ('response' is used for everything that will be used as input to other LLMs)
        # add prompt to response
        response['prompt'] = prompt
        
        if verbose:
            print('===================================')
            print(f'META')
            print('Prompt: ', prompt)
            print('Response: ', response)

        return response