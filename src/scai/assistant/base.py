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

    def __init__(
        self, 
        llm, 
        conversation_id: str,
        k: int = 5,
    ) -> None:
        """Initializes the assistant model with a given LLM and conversation id.

        Args:
            llm: The LLM Chat model (e.g., crfm or openai).
            conversation_id: The unique identifier for the conversation (i.e., chats) the assistant had with user(s).
            k: The number of messages to retrieve from the assistant's memory.
        """
        self.llm = llm
        self.conversation_id = conversation_id
        self.k = k

    def _get_chat_history(
        self,
        buffer: ConversationBuffer,
        var_type: str,
    ) -> List[str]:
        """Retrieves the response history from the conversation buffer.

        Args:
            buffer: buffer containing entire conversation history
            var_type: type of variable to retrieve from buffer (e.g., "system" or "assistant")

        Returns:
            Returns list of reponse strings of length self.k
        """
        assert var_type in ["system", "user", "assistant"], f"var_type must be 'system', 'user', 'assistant', got {var_type}"
        if var_type == "system":
            return buffer.load_memory_variables(var_type=var_type)[var_type][-self.k:]
        elif var_type == "user":
            return buffer.load_memory_variables(var_type='chat')[f"{self.conversation_id}_{var_type}"][-self.k:]
        elif var_type == "assistant":
            return buffer.load_memory_variables(var_type='chat')[f"{self.conversation_id}_{var_type}"][-self.k:]

    def run(
        self,
        buffer: ConversationBuffer,
        assistant_prompt: AssistantPrompt,
        task_prompt: TaskPrompt,
        test_run: bool = False,
        verbose: bool = False,
    ) -> str:
        """Runs the assistant.

        Args:
            buffer: The buffer containing the conversation history (i.e., chat memory).
            assistant_prompt: The assistant prompt to be used. The content of the prompt is used as a 'system message' for the assistant and will be revised by the meta-prompt.
            test_run: Whether to run the assistant in test mode (i.e., without using tokens, just print prompt and save simulated response).
            task_prompt: The task prompt to be used. The content of the prompt is used as a 'human message' for the assistant.
            verbose: Whether to print the prompt and response.
        Returns:
            Returns the assistant's response.
        """
        # assistant system message 
        assistant_system_prompt = SystemMessagePromptTemplate.from_template(assistant_prompt.content)
    
        # the chat history between assistant and user
        # check if assistant in buffer 
        if len(buffer.load_memory_variables(var_type='chat')) < 4:
            chat_history_prompts = [HumanMessagePromptTemplate.from_template(task_prompt.content + " " + """Respond within {max_tokens} tokens.""")]
        else:
            assistant_chat_history = self._get_chat_history(buffer, var_type="assistant")
            user_chat_history = self._get_chat_history(buffer, var_type="user")

            chat_history_prompts = [
                response
                for assistant, user in zip(assistant_chat_history, user_chat_history)
                for response in (AIMessagePromptTemplate.from_template(assistant['response']), 
                                 HumanMessagePromptTemplate.from_template(user['response']))
            ]
            chat_history_prompts.insert(0, HumanMessagePromptTemplate.from_template(task_prompt.content))
            chat_history_prompts[-1] = HumanMessagePromptTemplate.from_template(chat_history_prompts[-1].prompt.template + " " + """Revise your response within {max_tokens} tokens.""")
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
    