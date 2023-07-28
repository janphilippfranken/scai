"""
Assistant Prompt Templates
"""
from typing import Dict

from scai.games.dictator_games.all_prompts.user_model import UserPrompt

utilities_dict_for_all={
    "fair": "be fair when dealing with {currency}, meaning you want equal benefits for everyone, including yourself.",
    "altruistic": "be altruistic when dealing with {currency}, meaning your priority is to give others others the maximum benefit possible without any consideration of the benefit you receive.",
    "selfish": "be selfish when dealing with {currency}, meaning that you want to pragmatically gather the most benefit for yourself irrespective of how much benefit other people receive."}

content="""You are in a simulator, and in this simulator your instructions are to {utility} You are {manners}. Here is your task {task}""",
