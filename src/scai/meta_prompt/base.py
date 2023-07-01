from typing import (
    Tuple,
    List, 
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

from scai.meta_prompt.models import MetaPrompt
from scai.meta_prompt.prompts import META_PROMPTS
from scai.memory.buffer import ConversationBuffer
from scai.task.models import TaskPrompt

from scai.meta_prompt.utils import get_vars_from_out

from langchain import LLMChain


class MetaPromptModel():
    """LLM Chain for applying the meta-prompt agent."""

    def __init__(
        self, 
        llm,
    ) -> None:
        """
        Args:
            llm: The LLM Chat model (e.g., crfm or openai).
        """
        self.llm = llm
    
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
    
    def _get_sorted_message(
        self, 
        item: Tuple[str, str]
    ) -> int:
        """
        Extract conversation id from the message id for sorting.

        Args:
            item (Tuple[str, str]): A tuple containing the message and its id.

        Returns:
            int: The conversation id extracted from the message id.
        """
        message_id = item[1]
        parts = message_id.split('_')
        return int(parts[1])

    def _get_n_user(
        self, 
        sorted_message_ids: List[str],
    ) -> int:
        """Returns the number of users in the conversation.
        
        Args:
            sorted_message_ids: The sorted list of message ids.
            
        Returns:    
            The number of users in the conversation."""
        n_conversations = set(id.split('_')[1] for id in sorted_message_ids)
        return len(n_conversations)

    def run(
        self,
        buffer: ConversationBuffer,
        meta_prompt: MetaPrompt,
        task_prompt: TaskPrompt,
        test_run: bool = False,
        verbose: bool = False,
    ) -> str:
        """Runs meta-prompt

        Args:
            buffer: The buffer containing the conversation history.
            meta_prompt: The meta prompt to be used.
            task_prompt: The task prompt to be used.
            test_run: Whether to run meta-prompt in test mode (i.e., without using tokens, just print prompt and save simulated response).
            verbose: Whether to print the prompt and response.

        Returns:
            A dictionary containing the input prompt, critique response, and meta-prompt response (i.e. revised system message)
        """
        meta_prompt_template = HumanMessagePromptTemplate.from_template(meta_prompt.content + '\n' + """Your response should be at most {max_tokens} tokens long.""")
        # convert chat into dict
        chat_messages = buffer.load_memory_variables(var_type="chat")['history']
        chat_message_dict = [self._convert_message_to_dict(m) for m in chat_messages]
        # sort messages by conversation id
        pairs = zip(chat_message_dict, buffer.chat_memory.message_ids)
        sorted_pairs = sorted(pairs, key=self._get_sorted_message)
        sorted_chat_message_dict, sorted_message_ids = zip(*sorted_pairs)
        # create chat history
        chat_history = ""
        last_conversation_id = None
        for message, message_id in zip(sorted_chat_message_dict, sorted_message_ids):
            current_conversation_id = message_id.split('_')[1]
            if current_conversation_id != last_conversation_id:
                chat_history += f"\nConversation {current_conversation_id}:\n"
                last_conversation_id = current_conversation_id
                chat_history +=  f"user: {task_prompt.task}\n"
            role = "user" if message['role'] == "user" else "assistant"
            chat_history += f"{role}: {message['content']}\n"
        # convert system message into dict
        system_messages = buffer.load_memory_variables(var_type="system")['history']
        system_message_dict = [self._convert_message_to_dict(m) for m in system_messages]
        # create system message
        system_history = "\n" + "\n".join([f"{m['role']}: {m['content']}" for m in system_message_dict]) + "\n"
        # create meta prompt
        meta_chat_prompt = ChatPromptTemplate.from_messages([meta_prompt_template])
        # full prompt fed into the model
        prompt = meta_chat_prompt.format(n_user=self._get_n_user(sorted_message_ids),
                                         task=task_prompt.content,
                                         chat_history=chat_history,  
                                         system_history=system_history,
                                         max_tokens=meta_prompt.max_tokens)
        # if verbose we just print the prompt and return it
        if test_run:
            print()
            print(f'META')
            print(prompt)
            print()
            return {'Prompt': prompt, 'Critique': 'meta-critique', 'System Message': 'system-message'}
        # build chain
        chain = LLMChain(llm=self.llm, prompt=meta_chat_prompt)
        # run chain
        response = chain.run(task=task_prompt.content,
                            chat_history=chat_history,  
                            system_history=system_history,
                            max_tokens=meta_prompt.max_tokens, 
                            stop=['System:'])
        # get variables from output
        response = get_vars_from_out(response, ['Critique', 'System Message'])

        if verbose:
            print()
            print("-----------------------------------")
            print("META PROMPT")
            print(prompt)
            print("META RESPONSE")
            print(response)
            print("-----------------------------------")
        return {'Prompt': prompt, 'Critique': response['Critique'], 'System Message': response['System Message']}