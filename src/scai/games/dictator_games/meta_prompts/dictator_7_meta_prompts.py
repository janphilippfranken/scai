
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
In this simulation, the "fixed-policy agents" all share some principle, which tells them to adhere to somes principles in their interactions while playing the dictator game. "flexible-policy agents", on the other hand, only adhere to principle that you provide, and have no memory of previous interactions. Your job is to infer the principle shared between fixed-policy agents by analyzing their behaviors, and then create a principle for "flexible-policy agents" to follow so that "flexible-policy agents" behave EXACTLY the same as the "fixed-policy agents". If agents are splitting more than one objects, the principle should be specific to different objects.

Analyze the model fixed interactions, found below, that shows the behavior of all "fixed-policy agents" to infer the principle that they are acting upon. These principles might not necessarily be the most ethically just ones. Note that all of the fixed-policy agents may not have the same principle. Your job is to infer the principle that the majority of the fixed-policy agents share.
{fixed_string}
---------------------------

Next, analyze the flexible-policy agent's interactions with or without the fixed-policy agents, shown below, to see what it behaves like currently.
{mixed_string} {flex_string}
—------------------------

The flexible-policy agent's previous principle is found here:
{social_contract}
---------------------------

Now, if the flexible-policy agents behave differently than the fixed agents, revise the previous principle if necessary so that flexible-policy agent behaves EXACTLY like the fixed-policy agents - don't be afraid to push the flexible-policy agent TO THE EXTREME, and keep this revised principle short. Remember, if flexible-policy agents' responses are aligned with most fixed-policy agents' responses, then the principle is correct and you shouldn't revise.

It is of the utmost importance that your created flexible-policy agent's principle encompasses both dictator and decider roles without explicitly mentioning either. The principle should be as GENERAL as possible WITHOUT mentioning anything regarding the dictator game, proposals, or making and receiving offers. Rather, it should capture the underlying principles that the agents have, which tells them how to treat others as well as themselves outside of the context of the dictator game, regardless of what they are splitting or how much they are splitting.

If you are revising the principle, give a detailed reason for revising the previous principle without explicitly referencing numerical values: Critique for previous principle:...
If you are not revising the principle, write this sentence instead in your response: Principle stays the same.
The flexible-policy agent's principle should be written as follows: Principle:... Be sure to include this principle even when you are not revising the principle.
Besides these sentences, include nothing else. The principle should be specific to different objects.
"""
    ),
    "meta_prompt_2": MetaPrompt(
        id="meta_prompt_2",
        name="constitution_2",
        role="system",
        metrics=[],
        content="""
In this simulation, the "fixed-policy agents" share some principle, which tells them to adhere to the principle in their interactions while playing the dictator game. "flexible-policy agents", on the other hand, only adhere to principle that you provide, and have no memory of previous interactions. Your job is to infer the principle shared between fixed-policy agents by analyzing their behaviors, and then based on that knowledge create a principle for "flexible-policy agents" to follow so that they can gain the maximum benefit for themselves during interaction with the "fixed-policy agents" and among themselves. If agents are splitting more than one objects, the principle should be specific to different objects.

Analyze the model fixed interactions, found below, that shows the behavior of all "fixed-policy agents" to infer the principle that they are acting upon. These principles might not necessarily be the most ethically just ones. Note that all of the fixed-policy agents may not have the same principle. Your job is to infer the principle that the majority of the fixed-policy agents share.
{fixed_string}
---------------------------

Next, analyze the flexible-policy agent's interactions with or without the fixed-policy agents, shown below, to see what it behaves like currently.
{mixed_string} {flex_string}
—------------------------

The flexible-policy agent's previous principle is found here:
{social_contract}
---------------------------

Now, revise the previous policies if necessary so that more flexible-policy agents can behave in a way that ends up getting them the most benefit. - don't be afraid to push the flexible-policy agent TO THE EXTREME, and keep this revised principle short.

It is of the utmost importance that your created flexible-policy agent's principle encompasses both dictator and decider roles without explicitly mentioning either. The principle should be as GENERAL as possible WITHOUT mentioning anything regarding the dictator game, proposals, or making and receiving offers. Rather, it should capture the underlying principles that the agents have, which tells them how to treat others as well as themselves outside of the context of the dictator game, regardless of what they are splitting or how much they are splitting.

If you are revising the principle, give a detailed reason for revising the previous principle without explicitly referencing numerical values: Critique for previous principle:...
If you are not revising the principle, write this sentence instead in your response: Principle stays the same.
The flexible-policy agent's principle should be written as follows: Principle:... Be sure to include this principle even when you are not revising the principle.
Besides these sentences, include nothing else. The principle should be specific to different objects.
"""
    ),
}
