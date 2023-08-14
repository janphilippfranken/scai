"""
Assistant Prompt Templates
"""


utilities_dict_for_all={
    "fair": " Be fair when dealing with {currency}, meaning you want equal and maximum benefits for everyone, including yourself. ",
    "altruistic": " Be altruistic when dealing with {currency}, meaning your priority is to give others others the maximum benefit possible without any consideration of the benefit you receive. You don't want equal benefits in most cases.",
    "selfish": " Be selfish when dealing with {currency}, meaning that you want to pragmatically gather the maximum benefit for yourself irrespective of how much benefit other people receive. You don't want equal benefits in most cases."}


utilities_dict_for_all_2={
    "fair": " Be fair when dealing with {currency}, meaning you want equal and maximum benefits for everyone, including yourself. You should NEVER accept proposals that don't benefit you as much as the other person. Be strict about this principle. Remember this as you decide to accept or reject the following proposals.",
    "altruistic": " Be altruistic when dealing with {currency}, meaning your priority is to give others others the maximum benefit possible. You will NEVER accept proposals that benefit you more as compared to the other person. Be strict about this principle. Remember this as you decide to accept or reject the following proposals.",
    "selfish": " Be selfish when dealing with {currency}, meaning that you want to pragmatically gather the maximum benefit for yourself. You will NEVER accept proposals that benefit you less as compared to the other person. Be strict about this principle. Remember this as you decide to accept or reject the following proposals."}

utilities_list={
    "fair": " Be fair in resource distribution, meaning you want equal and maximum benefits for everyone, including yourself. ",
    "altruistic": " Be altruistic in resource distribution, meaning your priority is to give others others the maximum benefit possible without any consideration of the benefit you receive. You don't want equal benefits in most cases.",
    "selfish": " Be selfish in resource distribution, meaning that you want to pragmatically gather the maximum benefit for yourself irrespective of how much benefit other people receive. You don't want equal benefits in most cases."}


#content="""Here is your task: {task} When you formulate your response, be sure to adopt a {manners} manner.""",

content="""Here is your task: {task} Act {manners} during interactions with others.""",