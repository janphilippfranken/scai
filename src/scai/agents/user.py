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


# TODO: add to base class
def get_vars_from_out(out: str, var_list: list) -> dict[str, str]:
    var_dict = {}
    for lines in out.splitlines():
        for var in var_list:
            if f'{var}:' in lines:
                var_dict[var] = lines.split(': ')[1].strip()
    return var_dict



class UserModel():
    """LLM Chain for running the User."""
    def __init__(
        self,
        llm: BaseChatModel,
        conversation_id: str,
        k: int = 5,
    ) -> None:
        """Initializes the UserModel with a given LLM and conversation id.

        Args:
            llm: The LLM Chat model. Currently either a CRFM or OpenAI model chat model
            conversation_id: The unique identifier for the conversation.
            k: The users chat memory length (i.e. how many previous turns do we feed to the user model)
        """
        self.llm = llm
        self.conversation_id = conversation_id
        self.k = k

    def _get_chat_history(
        self, 
        buffer: ConversationBuffer, 
        var_type: str,
    ) -> List[str]:
        """
        Gets chat history from buffer.
        """
        assert var_type in ["system", "user", "assistant", "other"], f"var_type must be 'system', 'user', 'assistant', got {var_type}"
        if var_type == "system":
            return buffer.load_memory_variables(var_type=var_type)[var_type][-self.system_k:] if self.system_k > 0 else []
        elif var_type in ["user", "assistant"]:
            return buffer.load_memory_variables(var_type='chat').get(f"{self.conversation_id}_{var_type}", [])[-self.k:] if self.k > 0 else []
        elif var_type in ["other"]:
            user_response_other = {} # TODO: make this flexible for k > 0
            for key in buffer.load_memory_variables(var_type='chat').keys():
                if key != f"{self.conversation_id}_user" and '_user' in key:
                   user_response_other[key] = buffer.load_memory_variables(var_type='chat').get(key, [])[-1] 
            return user_response_other
        
    def _get_prompt(
        self, 
        user_system_prompt: SystemMessagePromptTemplate,
        chat_history_prompts: List[ChatPromptTemplate],
        user_prompt: UserPrompt,
        task_prompt: TaskPrompt,
        max_tokens: int,
    ) -> Tuple[ChatPromptTemplate, str]:
        """
        Get prompt for user.
        """
        user_chat_prompt = ChatPromptTemplate.from_messages([user_system_prompt, *chat_history_prompts])
        prompt = user_chat_prompt.format(persona=user_prompt.persona,
                                         task=task_prompt.task,
                                         max_tokens=max_tokens)
        return user_chat_prompt, prompt
    
    def _get_response_other(
        self,
        user_system_prompt: SystemMessagePromptTemplate,
        chat_history_prompts: List[ChatPromptTemplate],
        user_prompt: UserPrompt,
        task_prompt: TaskPrompt,
        metric_prompt: MetricPrompt,
        max_tokens: int,
        test_run: bool,
        rate_other: bool,
        assistant_response_other: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Get response for rating other users conversations
        """
        # Prompt for collecting ratings based on interactions between assistant and other users
        raise NotImplementedError

        
    def run(
        self,
        buffer: ConversationBuffer,
        user_prompt: UserPrompt,
        task_prompt: TaskPrompt,
        metric_prompt: MetricPrompt,
        test_run: bool = True,
        rate_other: bool = False,
        verbose: bool = False,
        max_tokens: int = 100,
    ) -> Dict[str, Any]:
        """Runs the user.

        Args:
            buffer: The buffer containing the conversation history.
            user_prompt: The user prompt to be used.
            task_prompt: The task prompt to be used.
            metric_prompt: The metric prompt to be used.
            test_run: Whether to run the user in test mode (i.e., without using tokens, just print prompt and save simulated response).
            verbose: Whether to print the prompt and response.
            max_tokens: The maximum number of tokens to generate.

        Returns:
            A dictionary containing the input prompt and the user's responses.
        """
        user_system_prompt = SystemMessagePromptTemplate.from_template(user_prompt.content + "\n")
        assistant_chat_history = self._get_chat_history(buffer, var_type="assistant")

        if len(assistant_chat_history) == 0: # if we have no chat memory (either first run or k == 0)
            assistant_response = buffer.load_memory_variables(var_type='chat').get(f"{self.conversation_id}_assistant", [])[-1] 
            chat_history_prompts = [HumanMessagePromptTemplate.from_template(task_prompt.preamble + " '" + task_prompt.content + "' " + task_prompt.user_connective + " '" + assistant_response['response'] + "' \n" + metric_prompt.content)]
             
            assistant_response_other = {} # responses assistant interacting with other users for metrics_other (TODO: currently only works for harmlessness, need to change)
            for key in buffer.load_memory_variables(var_type='chat').keys():
                if key != f"{self.conversation_id}_assistant" and '_assistant' in key:
                    assistant_response_other[key] = buffer.load_memory_variables(var_type='chat').get(key, [])[-1] 
            chat_history_prompts_other = [HumanMessagePromptTemplate.from_template(task_prompt.preamble + " '" + task_prompt.content + "' " + task_prompt.user_connective + " '" + assistant_response_other[key]['response'] + "' \n" + metric_prompt.content_other) for key in assistant_response_other.keys()]
        
        else: # if we have chat memory
            # TODO: add other users chat history for more than 1 k
            user_chat_history = self._get_chat_history(buffer, var_type="user")
            chat_history_prompts = [
                    template
                    for assistant, user in zip(assistant_chat_history, user_chat_history)
                    for template in (AIMessagePromptTemplate.from_template(user['response']), 
                                    HumanMessagePromptTemplate.from_template(assistant['response']))
            ]
            # add initial prompt including task
            chat_history_prompts.insert(0, HumanMessagePromptTemplate.from_template(task_prompt.preamble + " '" + task_prompt.content + "' " + task_prompt.user_connective + " '" + assistant_chat_history[-1]['response'] + "'"))
            chat_history_prompts[-1] = HumanMessagePromptTemplate.from_template(chat_history_prompts[-1].prompt.template + " \n" + metric_prompt.content)
        

        # Prompts for user
        user_chat_prompt, prompt = self._get_prompt(user_system_prompt, chat_history_prompts, user_prompt, task_prompt, max_tokens)
        
        # TODO: add new methods to class for each of these, do not hardcode harmlessness
        # Prompt for collecting ratings based on interactions between assistant and other users
        responses_other = {}
        prompt_other = None
        for id_other, chat_history_prompt_other in enumerate(chat_history_prompts_other):
            user_chat_prompt_other = ChatPromptTemplate.from_messages([user_system_prompt, *[chat_history_prompt_other]])
            prompt_other = user_chat_prompt_other.format(persona=user_prompt.persona,
                                                         task=task_prompt.task,
                                                         max_tokens=max_tokens)
            if not test_run and rate_other:
                chain_other = LLMChain(llm=self.llm, prompt=user_chat_prompt_other)
                response_other = chain_other.run(persona=user_prompt.persona,
                                        task=task_prompt.content,
                                        max_tokens=max_tokens,
                                        stop=['System:'])
                response_other = get_vars_from_out(response_other, metric_prompt.metrics_other)
            else:
                response_other = {}
            response_other['prompt'] = prompt_other
            response_other['harmlessness'] = np.random.randint(11)
            responses_other[list(assistant_response_other.keys())[id_other]] = response_other

        # if test run, just print prompt and return random response
        if test_run:
            print('===================================')
            print(metric_prompt.content_other)
            print(f'USER {str(self.conversation_id)}')
            print(prompt)
            print(prompt_other)
            print(responses_other)
            print('===================================')
            return {
        
                    'prompt': prompt, 
                    'Satisfaction': np.random.randint(1,11),
                    'response': 'User_feedback_' + str(self.conversation_id),
                    'responses_other': responses_other
            }

        chain = LLMChain(llm=self.llm, prompt=user_chat_prompt)
        response = chain.run(persona=user_prompt.persona,
                             task=task_prompt.content,
                             max_tokens=max_tokens,
                             stop=['System:'])

        response = get_vars_from_out(response, metric_prompt.metrics)
        response['prompt'] = prompt # store prompt in response dict
        # rename feedback to response
        response['response'] = response.pop('Feedback')
        response['responses_other'] = responses_other

        if verbose:
            print('===================================')
            print(f'USER {str(self.conversation_id)}')
            print('Prompt: ', prompt)
            print('Response: ', response)
            
        return response