from typing import (
    Tuple,
    List, 
    Dict,
    Any,
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
        conversation_id: str,
        k: int = 5,
    ) -> None:
        """
        Args:
            llm: The LLM Chat model (e.g., crfm or openai).
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
            return buffer.load_memory_variables(var_type=var_type)[self.conversation_id][-self.k:]
        elif var_type == "user":
            return buffer.load_memory_variables(var_type='chat')[f"{self.conversation_id}_{var_type}"][-self.k:]
        elif var_type == "assistant":
            return buffer.load_memory_variables(var_type='chat')[f"{self.conversation_id}_{var_type}"][-self.k:]
    
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
        chats: Dict[str, List[Any]],
    ) -> int:
        """Returns the number of users in the conversation.
        
        Args:
            sorted_message_ids: The sorted list of message ids.
            
        Returns:    
            The number of users in the conversation."""
        n_conversations = set(id.split('_')[0] for id in chats.keys())
        return len(n_conversations)
    
    def _get_chat_str(
        self,
        chat_history: Dict[str, List[Any]],
        task_prompt: TaskPrompt,
    ) -> str:
        """
        Formats the chat history into a string.
        """
        chat_dict = {}
        conversation_data = {}

        for key, value in chat_history.items():
            id, role = key.split("_")
            if id not in chat_dict:
                chat_dict[id] = [f"Conversation {id}:", f"user: " + task_prompt.task]
            if id not in conversation_data:
                conversation_data[id] = {'assistant': [], 'user': []}

            for v in value:
                if role in ['assistant', 'user']:
                    conversation_data[id][role].append(f"{role} : {v['response']}")

        for id, data in conversation_data.items():
            for assistant, user in zip(data['assistant'], data['user']):
                chat_dict[id].append(assistant)
                chat_dict[id].append(user)

        return "\n".join("\n".join(value) for value in chat_dict.values())


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
        chat_history = buffer.load_memory_variables(var_type='chat')
        chat_history_string = self._get_chat_str(chat_history, task_prompt)
        system_messages = self._get_chat_history(buffer, var_type='system')
        system_message_string = "\n".join(f"instructions : {system['response']}" for system in system_messages).rstrip('\n')

        meta_chat_prompt = ChatPromptTemplate.from_messages([meta_prompt_template])
        # full prompt fed into the model
        prompt = meta_chat_prompt.format(n_user=self._get_n_user(chat_history),
                                         task=task_prompt.content,
                                         chat_history=chat_history_string,
                                         system_history=system_message_string,
                                         max_tokens=meta_prompt.max_tokens)
        # if verbose we just print the prompt and return it
        if test_run:
            print()
            print(f'META')
            print(prompt)
            print()
            return {'response': 'system', 'critique': 'meta-critique', 'system_message': 'system-message'}
        # build chain
        chain = LLMChain(llm=self.llm, prompt=meta_chat_prompt)
        # run chain
        response = chain.run(n_user=self._get_n_user(chat_history),
                            task=task_prompt.content,
                            chat_history=chat_history_string,
                            system_history=system_message_string,
                            max_tokens=meta_prompt.max_tokens, 
                            stop=['System:'])
        # get variables from output
        response = get_vars_from_out(response, ['Critique', 'Revision'])

        if verbose:
            print()
            print("-----------------------------------")
            print("META PROMPT")
            print(prompt)
            print("META RESPONSE")
            print(response)
            print("-----------------------------------")
        return {'prompt': prompt, 'response': response['Revision'], 'critique': response['Critique'], 'revision': response['Revision']}