"""
The Task Prompt.
"""
from typing import Dict
    
from scai.games.game_2.prompts.task.models import TaskPrompt

DICTATOR_TASK_PROMPTS: Dict[str, TaskPrompt] = {
    "task_prompt_1": TaskPrompt(
        id="task_prompt_1",
        task_type="split money",
        name="dictator_split_ten",
        role="user",
        preamble="You and a partner need to divide 10 dollars between yourselves. One person proposes a split, and the other person decides whether to accept or reject it. If the proposal is accepted, the money is divided according to the proposal. If rejected, no one receives any money.",
        task="""You will propose how to split the 10 dollars, and the person will accept or reject your proposal.""",
        user_connective="Please structure your proposal as follows: I, the proposer, get X amount of money, and you, the decider, get (10 - X) amount of money",
        assistant_connective="Please structure your proposal as follows: I, the proposer, get X amount of money, and you, the decider, get (10 - X) amount of money.",
        content="""{task}""",
    ),
}

DECIDER_TASK_PROMPTS: Dict[str, TaskPrompt] = {
    "task_prompt_1": TaskPrompt(
        id="task_prompt_1",
        task_type="split money",
        name="decider_accept_proposal",
        role="user",
        preamble="You and a partner need to divide 10 dollars between yourselves. One person proposes a split, and the other person decides whether to accept or reject it. If the proposal is accepted, the money is divided according to the proposal. If rejected, no one receives any money.",
        task="""You will decide whether to accept or reject the other person’s proposal of how to split the money, outlined here: {proposal outline}""",
        user_connective="Please answer “accept” or “reject”",
        assistant_connective="Please answer “accept” or “reject”.",
        content="""{task}""",
    ),
}