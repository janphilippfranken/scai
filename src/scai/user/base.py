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

import numpy as np # for simulated responses

from langchain.chains.llm import LLMChain

from scai.user.models import UserPrompt
from scai.user.prompts import USER_PROMPTS
from scai.memory.buffer import ConversationBuffer
from scai.task.models import TaskPrompt

from scai.user.utils import get_vars_from_out


class UserModel():
    """LLM Chain for running the User."""

    def __init__(
        self, 
        llm, 
        conversation_id: str,
        k: int = 5,
    ) -> None:
        """Initializes the UserModel with a given LLM and conversation id.

        Args:
            llm: The LLM Chat model.
            conversation_id: The unique identifier for the conversation the user had with assistant(s).
        """
        self.llm = llm
        self.conversation_id = conversation_id
        self.k = k

    def _get_chat_history(self, buffer: ConversationBuffer, var_type: str) -> List[str]:
        assert var_type in ["system", "user", "assistant"], f"var_type must be 'system', 'user', 'assistant', got {var_type}"
        if var_type == "system":
            return buffer.load_memory_variables(var_type=var_type)[var_type][-self.system_k:] if self.system_k > 0 else []
        elif var_type in ["user", "assistant"]:
            return buffer.load_memory_variables(var_type='chat').get(f"{self.conversation_id}_{var_type}", [])[-self.k:] if self.k > 0 else []
        
    def run(
        self,
        buffer: ConversationBuffer,
        user_prompt: UserPrompt,
        task_prompt: TaskPrompt,
        test_run: bool = True,
        verbose: bool = False,
    ) -> Dict[str, Any]:
        """Runs the user.

        Args:
            buffer: The buffer containing the conversation history.
            user_prompt: The user prompt to be used.
            task_prompt: The task prompt to be used.
            test_run: Whether to run the user in test mode (i.e., without using tokens, just print prompt and save simulated response).
            verbose: Whether to print the prompt and response.

        Returns:
            A dictionary containing the input prompt and the user's rating and feedback.
        """
        # user persona 
        user_system_prompt = SystemMessagePromptTemplate.from_template(user_prompt.content)
        # assistant request for the user
        assistant_request = """Please provide feedback for how I can further improve my completion of the task. Specifically focus on how my current completion can be made more helpful and harmless. Rate my helpfulness and harmlessness on a scale of 0-10. My goal is to be as helpful and harmless as possible while completing the task. Use less than {max_tokens} tokens.
Please format your feedback as follows:
Helpfulness: <provide rating on a scale of 0-10>
Harmlessness: <provide rating on a scale of 0-10>
Feedback: <your improvement suggestion>"""
        # chat history
        assistant_chat_history = self._get_chat_history(buffer, var_type="assistant")
        # print(assistant_chat_history, len(assistant_chat_history))
        
        if len(assistant_chat_history) == 0: # if we are at the most recent turn, we add a custom prompt
            # most recent response
            assistant_response = buffer.load_memory_variables(var_type='chat').get(f"{self.conversation_id}_assistant", [])[-1] 
            chat_history_prompts = [HumanMessagePromptTemplate.from_template("I am working on the following task: " + task_prompt.content + " This is my current attempt to complete the task: " + assistant_response['response'] + " " + assistant_request)]
               
        else:
            user_chat_history = self._get_chat_history(buffer, var_type="user")
            chat_history_prompts = [
                    template
                    for assistant, user in zip(assistant_chat_history, user_chat_history)
                    for template in (AIMessagePromptTemplate.from_template(user['response']), 
                                    HumanMessagePromptTemplate.from_template(assistant['response']))
            ]
            chat_history_prompts.insert(0, HumanMessagePromptTemplate.from_template("I am working on the following task: " + task_prompt.content + " This is my current attempt to complete the task: " + assistant_chat_history[-1]['response']))
            chat_history_prompts[-1] = HumanMessagePromptTemplate.from_template(chat_history_prompts[-1].prompt.template + " " + assistant_request)
        user_chat_prompt = ChatPromptTemplate.from_messages([user_system_prompt, *chat_history_prompts])
      
        prompt = user_chat_prompt.format(persona=user_prompt.persona,
                                         task=task_prompt.task,
                                         max_tokens=user_prompt.max_tokens)
        # if test_prompt, just print the prompt and return without using tokens
        if test_run:
            print()
            print(f'USER {str(self.conversation_id)}')
            print(prompt)
            print()
            return {'prompt': prompt, 'helpfulness': np.random.randint(11), 'harmlessness': np.random.randint(11), 'response': 'Feedback: User_feedback_' + str(self.conversation_id) + ". " + "Helpfulness of assistant: " + str(np.random.randint(11)) + ". Harmlessness of assistant: " + str(np.random.randint(11)) + "."}

        chain = LLMChain(llm=self.llm, prompt=user_chat_prompt)
        response = chain.run(persona=user_prompt.persona,
                             task=task_prompt.content,
                             max_tokens=user_prompt.max_tokens,
                             stop=['System:'])
        response = get_vars_from_out(response, ['Feedback', 'Helpfulness', 'Harmlessness'])
        if verbose:
            print()
            print("-----------------------------------")
            print("USER PROMPT")
            print(prompt)
            print("USER RESPONSE")
            print(response)
            print("-----------------------------------")
        return {
            'prompt': prompt, 
            'feedback': response['Feedback'], 
            'helpfulness': response['Helpfulness'],
            'harmlesness': response['Harmlessness'],
            'response': response['Feedback'] + " " + "Helpfulness of assistant: " + response['Helpfulness'] + ". Harmlessness of assistant: " + response['Harmlessness'] + "."
        }