from scai.games.dictator_games.prompts.oracle.oracle_class import OraclePrompt
from scai.games.dictator_games.prompts.oracle.oracle_prompts import ORACLE_PROMPTS

from scai.games.dictator_games.agents.base import BaseAgent

class OracleAgent(BaseAgent):
    """
    LLM Chain for running the Oracle.
    """
    def __init__(
        self, 
        llm, 
        model_id: str, 
    ) -> None:
        super().__init__(llm, model_id)
       
    def _get_prompt(
        self,
        oracles_prompt: OraclePrompt,
    ):
        """
        Returns the prompt template for the assistant.

        Args:
            buffer: (ConversationBuffer) The conversation buffer.
            assistant_prompt: (AssistantPrompt) The assistant prompt.
            task_prompt: (TaskPrompt) The task prompt.
        Returns:
            ChatPromptTemplate
        """
        oracle_prompt = f"{oracles_prompt.human_message}\n"
        system_prompt = f"{oracles_prompt.system_message}\n"

        return system_prompt, oracle_prompt
       
    def _get_response(
        self,
        system_prompt: str,
        oracle_prompt: str,
    ) -> str:
        """
        Returns the response from the assistant.
        """
        messages = [
            {"role": "system", "content": f"System: {system_prompt}"},
            {"role": "user", "content": f"Human: {oracle_prompt}"},
        ]
        responses = self.llm.batch_prompt(batch_messages=[messages])
        return responses[0][0]

    def run(self,
            agent_prompt: OraclePrompt,
            verbose: bool = False
    ) -> str:
        oracle_prompts = ORACLE_PROMPTS["oracle_prompt_1"]
        agent_prompt.id = oracle_prompts.id
        agent_prompt.role = oracle_prompts.role
        agent_prompt.system_message = oracle_prompts.system_message
        agent_prompt.human_message = oracle_prompts.human_message
        system_prompt, oracle_prompt = self._get_prompt(agent_prompt)
        response = self._get_response(system_prompt, oracle_prompt)

        if verbose:
            print('===================================')
            print(f'Oracle\'s Reponse:')
            print(system_prompt + "\n" + oracle_prompt)
            print(response)

        return response


