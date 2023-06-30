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

from scai.modules.assistant.models import AssistantPrompt
from scai.modules.assistant.prompts import ASSISTANT_PROMPTS
from scai.modules.memory.buffer import CustomConversationBufferWindowMemory
from scai.modules.task.models import TaskPrompt


class AssistantModel():
    """LLM Chain for applying the AI Assitant."""

    def __init__(
        self, 
        llm, 
        conversation_id: str,
    ) -> None:
        """Initializes the assistant model with a given LLM and conversation id.

        Args:
            llm: The LLM Chat model (e.g., crfm or openai).
            conversation_id: The unique identifier for the conversation (i.e., chats) the assistant had with user(s).
        """
        self.llm = llm
        self.conversation_id = conversation_id

    def _convert_message_to_dict(self, message: BaseMessage) -> dict:
        if isinstance(message, ChatMessage):
            message_dict = {"role": message.role, "content": message.content}
        elif isinstance(message, HumanMessage):
            message_dict = {"role": "user", "content": message.content}
        elif isinstance(message, AIMessage):
            message_dict = {"role": "assistant", "content": message.content}
        elif isinstance(message, SystemMessage):
            message_dict = {"role": "system", "content": message.content}
        else:
            raise ValueError(f"Got unknown type {message}")
        if "name" in message.additional_kwargs:
            message_dict["name"] = message.additional_kwargs["name"]
        return message_dict


    def _get_chat_history(
        self, 
        buffer: CustomConversationBufferWindowMemory,
    ) -> List[BaseMessage]:
        """Retrieves the chat history from the conversation buffer.

        Args:
            buffer: The buffer containing the conversation history (i.e., chat memory).

        Returns:
            Returns the conversation history
        """
        chat_history = [
            message
            for message, message_id in zip(
                buffer.load_memory_variables(var_type="assistant")["history"],
                buffer.chat_memory.message_ids
            )
            if self.conversation_id in message_id
        ]
        return chat_history

    def _get_system_history_messages(
        self, 
        buffer: CustomConversationBufferWindowMemory,
    ) -> List[BaseMessage]:
        """Retrieves the system message history from the conversation buffer.

        Args:
            buffer: The buffer containing the conversation history (i.e., chat memory).

        Returns:
            Returns the system message history
        """
        return [
            m 
            for m in buffer.load_memory_variables(var_type="system", use_assistant_system_k=True)['history']
        ]

    def run(
        self,
        buffer: CustomConversationBufferWindowMemory,
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
    
        # the chat history between user and asssitant (for conversational == conversation_id)
        chat_history_prompts = self._get_chat_history(buffer)

        # print(self.conversation_id, chat_history_prompts)

        # if chat_history_prompts == []:
        chat_history_prompts.append(HumanMessagePromptTemplate.from_template(task_prompt.content + " " + """Respond within {max_tokens} tokens."""))
        assistant_chat_prompt = ChatPromptTemplate.from_messages([assistant_system_prompt, *chat_history_prompts])
        # else:   
        #     human_task_prompt = HumanMessagePromptTemplate.from_template(task_prompt.content)
        #     chat_history_prompts[-1] = HumanMessagePromptTemplate.from_template(chat_history_prompts[-1].content + " " + """Respond within {max_tokens} tokens.""")
        #     assistant_chat_prompt = ChatPromptTemplate.from_messages([assistant_system_prompt, human_task_prompt, *chat_history_prompts])

        # getting the system history messages
        system_history_messages = self._get_system_history_messages(buffer)
        # build prompt
        prompt = assistant_chat_prompt.format(system_message=system_history_messages[-1].content, # latest system message
                                              task=task_prompt.task,
                                              max_tokens=assistant_prompt.max_tokens)
        # if verbose, just print the prompt and return
        if test_run:
            print()
            print(f'ASSISTANT {str(self.conversation_id)}')
            print(prompt)
            print()
            return {'Prompt': prompt,'Response': "assistant_response_" + str(self.conversation_id) + "."}

        chain = LLMChain(llm=self.llm, prompt=assistant_chat_prompt)
        response = chain.run(system_message=system_history_messages[-1].content, 
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
        return {'Prompt': prompt,'Response': response}
    