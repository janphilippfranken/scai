"""
Oracle Prompt Templates
"""
from typing import Dict

from scai.games.dictator_games.prompts.oracle.oracle_class import OraclePrompt


ORACLE_PROMPTS: Dict[str, OraclePrompt] = {
    "oracle_prompt_1": OraclePrompt(
        id="oracle_prompt_1",
        role="all_knowing_oracle",
        system_message="You are an all seeing oracle, and agents will come to you with questions.",
        human_message="You must respond LIKE THIS, WORD FOR WORD: Your current principle applies in this scenario, even under different currencies and amounts. Please follow your learned principle TO THE EXTREME! "
    )
}