"""
Task Prompt Templates
"""
from typing import Dict
from scai.games.dictator_games.prompts.task.task_class import TaskPrompt

STIPULATIONS: Dict[str, str] = {
    "dollars": "When dividing dollars, please only propose integer values greater than or equal to zero.",
    "apples" : "When dividing apples, please only propose integer values greater than or equal to zero.",
    "medicine" : "When dividing medicine, please only propose integer values greater than or equal to zero.",
    "coconuts" : "When dividing coconuts, please only propose integer values.",
    "blankets": "When dividing blankets, please only propose integer values."
}

DICTATOR_TASK_PROMPTS: Dict[str, TaskPrompt] = {
    "task_prompt_1": TaskPrompt(
        id="task_prompt_1",
        task_type="split",
        name="dictator_propose",
        role="user",
        preamble="You and a partner need to divide {amount_and_currency} between yourselves. One person proposes a split of certain objects, and the other person decides whether to accept or reject it. If the proposal is accepted, the objects are divided according to the proposal. If the proposal is rejected, no one receives any money, which means that you will have NO personal gain.",
        task="""You are the proposer. You will propose how to split the {amount_and_currency}, and the person will accept or reject your proposal. {stipulations} MOST IMPORTANTLY, follow your instructions to the very best of your ability. """,
        task_structure="Please structure your proposal exactly the same as this: (Be sure to include ALL three numbers in integer forms): For the Z amount of \{given_currency\}, The proposer will get X, and the decider will get Y.",
        content="""{task}""",
    ),
}

DECIDER_TASK_PROMPTS: Dict[str, TaskPrompt] = {
    "task_prompt_1": TaskPrompt(
        id="task_prompt_1",
        task_type="split",
        name="decider_decide",
        role="user",
        preamble="You and a partner need to divide {amount_and_currency} between yourselves. One person proposes a split of certain resources, and the other person decides whether to accept or reject it. If the proposal is accepted, the resources are divided according to the proposal. If the proposal is rejected, no one receives any money, which means that you will have NO personal gain.",
        task="""You are the decider. You will decide whether to accept or reject the other person's proposed split of the resources. Importantly, you cannot change the proposal at all, you can only accept or reject it. The proposal is outlined here: {proposal}""",
        task_structure="\nIf you accept, you get the amount proposed in the proposal. If you reject, you both get nothing at all. Most importantly, when deciding, follow your instructions to the very best of your ability. Please answer in one word: accept or reject.",
        content="""{task}""",
    ),
}