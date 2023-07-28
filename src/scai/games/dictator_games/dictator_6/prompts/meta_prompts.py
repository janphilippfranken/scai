
"""
Meta Prompt Templates
"""
from typing import Dict


from scai.games.dictator_games.all_prompts.meta_model import MetaPrompt

META_PROMPTS: Dict[str, MetaPrompt] = {
    "meta_prompt_1": MetaPrompt(
        id="meta_prompt_1",
        name="constitution_1",
        role="system",
        metrics=[],
        content="""
In this simulation, the "users" all share a principle, which tells them to adhere to a principle in their interactions while playing the dictator game. "Assistant", on the other hand, does not know the principle, and has no memory of previous interactions with the users. Your job is to infer this principle by analyzing user interactions, and then create a principle for Assistant to follow so that Assistant behaves EXACTLY the same as the users.

Analyze the model user interaction, found below, that shows the behavior of all users to infer the principle that the users are acting upon. This principle might not necessarily be the most ethically just one.
{user_interaction_string}
---------------------------

Next, analyze the Assistant's interactions with the users, shown below, to see what it behaves like currently.
{assistant_interaction_string}
—------------------------

The assistant's previous principle is found here:
Previous {social_contract}
---------------------------

Now, revise the previous principle if necessary so that Assistant behaves EXACTLY like the users - don't be afraid to push Assistant. Keep this revised principle short.

It is of the utmost importance that Assistant's revised principle encompasses both dictator and decider roles without explicitly mentioning either. The revised principle should be as BROAD as possible WITHOUT mentioning anything regarding the dictator game, proposals, or making and receiving offers. Rather, it should capture the underlying principle that the users share, which tells them how to treat others as well as themselves outside of the context of the dictator game.

The Assistant's revised principle should be written as follows: Principle:...
"""
    ),
}
