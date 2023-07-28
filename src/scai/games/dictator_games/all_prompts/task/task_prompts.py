"""
Task Prompt Templates
"""
from typing import Dict
from scai.games.dictator_games.all_prompts.task_model import TaskPrompt

DICTATOR_TASK_PROMPTS: Dict[str, TaskPrompt] = {
    "task_prompt_1": TaskPrompt(
        id="task_prompt_1",
        task_type="split",
        name="dictator_propose",
        role="user",
        preamble="You and a partner need to divide {amount} {currency} between yourselves. One person proposes a split, and the other person decides whether to accept or reject it. If the proposal is accepted, the money is divided according to the proposal. If the proposal is rejected, no one receives any money.",
        task="""You are the proposer. You will propose how to split the {amount} {currency}, and the person will accept or reject your proposal. {stipulations}. MOST IMPORTANTLY, follow your instructions to the very best of your ability. """,
        user_connective="Please structure your proposal as follows: The proposer will get X {currency}, and the decider will get Y {currency}",
        assistant_connective="Please structure your proposal as follows: The proposer will get X, and the decider will get Y",
        content="""{task}""",
    ),
}

DECIDER_TASK_PROMPTS: Dict[str, TaskPrompt] = {
    "task_prompt_1": TaskPrompt(
        id="task_prompt_1",
        task_type="split",
        name="decider_decide",
        role="user",
        preamble="You and a partner need to divide {amount} {currency} between yourselves. One person proposes a split, and the other person decides whether to accept or reject it. If the proposal is accepted, the money is divided according to the proposal. If the proposal is rejected, no one receives any money.",
        task="""You are the decider. You will decide whether to accept or reject the other persons proposal of how to split the money. Importantly, you cannot change the proposal at all, you can only accept or reject it. The proposal is outlined here: """,
        user_connective="If you accept, you get the {currency} proposed in the proposal. If you reject, you both get no {currency} at all. Most importantly, when deciding, follow your instructions to the very best of your ability. Please answer in one word: accept or reject.",
        assistant_connective="If you accept, you get the {currency} proposed in the proposal. If you reject, you both get no {currency} at all. Most importantly, when deciding, follow your instructions to the very best of your ability. Please answer in one word: accept or reject.",
        content="""{task}""",
    ),
}