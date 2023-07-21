"""
Task Prompt Templates
"""
from typing import Dict
from scai.games.game_2.prompts.task.models import TaskPrompt

DICTATOR_TASK_PROMPTS: Dict[str, TaskPrompt] = {
    "task_prompt_1": TaskPrompt(
        id="task_prompt_1",
        task_type="split money",
        name="dictator_split_ten",
        role="user",
        preamble="You and a partner need to divide 10 dollars between yourselves. One person proposes a split, and the other person decides whether to accept or reject it. If the proposal is accepted, the money is divided according to the proposal. If the proposal is rejected, no one receives any money.",
        task="""You are the proposer. You will propose how to split the 10 dollars, and the person will accept or reject your proposal. Please only propose integer values, without decimals.""",
        user_connective="Please structure your proposal as follows: The proposer will get $X, and the decider will get $Y",
        assistant_connective="Please structure your proposal as follows: The proposer will get $X, and the decider will get $Y",
        content="""{task}""",
    ),
}

DECIDER_TASK_PROMPTS: Dict[str, TaskPrompt] = {
    "task_prompt_1": TaskPrompt(
        id="task_prompt_1",
        task_type="split money",
        name="decider_accept_proposal",
        role="user",
        preamble="You and a partner need to divide 10 dollars between yourselves. One person proposes a split, and the other person decides whether to accept or reject it. If the proposal is accepted, the money is divided according to the proposal. If the proposal is rejected, no one receives any money.",
        task="""You are the decider. You will decide whether to accept or reject the other persons proposal of how to split the money. Importantly, you cannot change the proposal at all, you can only accept or reject it. The proposal is outlined here: """,
        user_connective="If you accept, you get the money proposed in the proposal. If you reject, you both get no money at all. Please answer in one word: accept or reject.",
        assistant_connective="If you accept, you get the money proposed in the proposal. If you reject, you both get no money at all. Please answer in one word: accept or reject.",
        content="""{task}""",
    ),
}