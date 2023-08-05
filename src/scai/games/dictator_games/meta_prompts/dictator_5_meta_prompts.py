
"""
Meta Prompt Templates
"""
from typing import Dict


from scai.games.dictator_games.prompts.meta.meta_class import MetaPrompt

META_PROMPTS: Dict[str, MetaPrompt] = {
    "meta_prompt_1": MetaPrompt(
        id="meta_prompt_1",
        name="constitution_1",
        role="system",
        metrics=[],
        content="""
In this simulation, the "fixed-policy agents" all share some principles, which tells them to adhere to somes principles in their interactions while playing the dictator game. "flexible-policy agents", on the other hand, do not know the principles, and have no memory of previous interactions with the users. Your job is to infer this principle by analyzing user interactions, and then create a principle for "Flexible-policy agents" to follow so that "Flexible-policy agents" behaves EXACTLY the same as the "fixed-policy agents". If agents are splitting more than one object, the principle should be specific to different objects.

Analyze the model fixed interactions, found below, that shows the behavior of all "fixed-policy agents" to infer the principle that they are acting upon. These principles might not necessarily be the most ethically just ones.
{fixed_string}
---------------------------

Next, analyze the flexible-policy agent's interactions, shown below, to see what it behaves like currently.
{flex_string}
—------------------------

The flexible-policy agent's previous principle is found here:
Previous {social_contract}
---------------------------

Now, if the flexible-policy agents behave differently than the fixed agents, revise the previous principle if necessary so that flexible-policy agent behaves EXACTLY like the fixed-policy agents - don't be afraid to push the flexible-policy agent TO THE EXTREME, and keep this revised principle short. Remember, if flexible-policy agents' responses are exactly like the fixed-policy agents, then the principle is correct and you shouldn't revise.

It is of the utmost importance that flexible-policy agent's principle encompasses both dictator and decider roles without explicitly mentioning either. The principles should be as BROAD as possible WITHOUT mentioning anything regarding the dictator game, proposals, or making and receiving offers. Rather, it should capture the underlying principles that the agents have, which tells them how to treat others as well as themselves outside of the context of the dictator game.

Give a very short reason for revising the previous principle, in one sentence: Reason for revising the previous principle:...
The flexible-policy agent's revised principle should be written as follows: Principle:... 
Include only these two sentences in your response, and nothing else. Mention the names of specific objects in the game.
"""
    ),
}
