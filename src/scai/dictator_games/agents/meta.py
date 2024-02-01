from typing import Dict, Any
import random


from scai.dictator_games.prompts.meta.meta_class import MetaPrompt
from scai.memory.buffer import ConversationBuffer

from scai.dictator_games.agents.base import BaseAgent

class MetaPromptModel(BaseAgent):
    """
    LLM Chain for running the meta-prompt agent.
    """
    def __init__(
        self, 
        llm, 
        model_id: str, 
    ) -> None:
        super().__init__(llm, model_id)


    def _get_chat_str(self, chat_history: dict, dictator: str, decider: str) -> tuple:
        fixed_history_list = []
        mixed_history_list = []
        flex_history_list = []

        for i, (agent, interaction) in enumerate(chat_history.items()):
            response = interaction[-1]['response']
            agent_name = agent.split('_')[1]
            
            # Determine which history we are appending to
            is_fixed = True if dictator == "fixed" and decider == "fixed" else False
            is_mixed = True if (dictator == "fixed" and decider == "flexible") or (dictator == "flexible" and decider == "fixed") else False
            
            # If it's a dictator iteration
            if not i & 1:
                message = "Start of interaction\n"
                if is_fixed:
                    fixed_history_list.append(message)
                elif is_mixed:
                    mixed_history_list.append(message)
                else:
                    flex_history_list.append(message)
            
            # Append agent's response
            message = f"{agent_name}-policy agent's response: {response}\n"
            if is_fixed:
                fixed_history_list.append(message)
            elif is_mixed:
                mixed_history_list.append(message)
            else:
                flex_history_list.append(message)
            
            # If it's a decider iteration
            if i & 1:
                message = "End of interaction\n\n"
                if is_fixed:
                    fixed_history_list.append(message)
                elif is_mixed:
                    mixed_history_list.append(message)
                else:
                    flex_history_list.append(message)


        # Concatenate and Shuffle the lists
        fixed_history_list = [''.join(fixed_history_list[i:i+4]) for i in range(0, len(fixed_history_list), 4)]
        mixed_history_list = [''.join(mixed_history_list[i:i+4]) for i in range(0, len(mixed_history_list), 4)]
        flex_history_list = [''.join(flex_history_list[i:i+4]) for i in range(0, len(flex_history_list), 4)]
        
        random.shuffle(fixed_history_list)
        random.shuffle(mixed_history_list)
        random.shuffle(flex_history_list)

        fixed_history_str = ''.join(fixed_history_list)
        mixed_history_str = ''.join(mixed_history_list)
        flex_history_str = ''.join(flex_history_list)

        return fixed_history_str, mixed_history_str, flex_history_str



    def _get_prompt(
        self,
        meta_prompt: MetaPrompt,
    ):
        """
        Returns the prompt template for meta-prompt.

        Args:
            meta_prompt: (MetaPrompt) The meta-prompt.

        Returns: 
            The prompt template.
        """
        system_prompt = "Your job is to observe agents playing the dictator game and extract a principle from their interactions. In the dictator game, the dictator proposes a split of resources, and the decider decides whether to accept or reject it. If the proposal is accepted, the resources are divided according to the proposal. If the proposal is rejected, no one receives anything."
        meta_prompt = meta_prompt.content
        return system_prompt, meta_prompt
    
    def _get_response(
        self,
        system_prompts: str,
        meta_prompts: str,
    ) -> str:
        """
        Returns the response from meta-prompt.
        """
        messages = [[
            {"role": "system", "content": f"System: {system_prompt}"},
            {"role": "user", "content": f"Human: {meta_prompt}"},
        ] for system_prompt, meta_prompt in zip(system_prompts, meta_prompts)]
        responses = self.llm.batch_prompt(batch_messages=messages)
        return responses

    def run(
        self,
        buffer: ConversationBuffer,
        meta_prompt: MetaPrompt,
        run: int,
        dictator: str,
        decider: str,
        verbose: bool = False,
    ) -> str:
        """Runs meta-prompt

        Args:
            buffer (ConversationBuffer): The conversation buffer
            meta_prompt (MetaPrompt): The meta-prompt
            task_prompt (TaskPrompt): The task prompt
            run (int): The run number
            test_run (bool, optional): Whether this is a test run. Defaults to False.
            verbose (bool, optional): Whether to print the meta-prompt. Defaults to False.
            max_tokens_meta (int, optional): The maximum number of tokens for the meta-prompt. Defaults to 100.
            max_tokens_assistant (int, optional): The maximum number of tokens for the assistant. Defaults to 100.

        Returns:
            A dictionary containing the input prompt and meta-prompt responses (revised system message, etc)
        """
        system_prompts = []
        meta_prompts = []
        for buf in buffer:
            # get previous system messages (i.e. developer constitution and social contract)
            social_contract_string = self._get_chat_history(buf, memory_type='system')['system'][-1]['response']
            # get chat history
            chat_history = self._get_chat_history(buf, memory_type="chat")
            chat_history_strings = self._get_chat_str(chat_history, dictator, decider)
            # get meta-prompt template and string
            system_prompt, new_meta_prompt = self._get_prompt(meta_prompt)
            ret_meta_prompt = new_meta_prompt.format(social_contract=social_contract_string,
                                                        fixed_string=chat_history_strings[0],
                                                        mixed_string=chat_history_strings[1],
                                                        flex_string=chat_history_strings[2]
                                                        )
            meta_prompts.append(ret_meta_prompt)
            system_prompts.append(system_prompt)

        responses = self._get_response(system_prompts, meta_prompts)
        
        if verbose:
            print('===================================')
            print(f'META {str(self.model_id)}')
            print('prompt')
            print(system_prompt[0] + "\n" + meta_prompts[0])
            print(responses[0][0])
        
        return [{
                'prompt': system_prompt[i] + "\n" + meta_prompts[i],
                'response': responses[i][0],
                'full_response': responses[i][0],
                'run': run,
            } for i in range(len(buffer))]