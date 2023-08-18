
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
In this simulation, the "fixed-policy agents" share some principle, which tells them to adhere to the principle in their interactions while playing the dictator game. "flexible-policy agents", on the other hand, only adhere to principle that you provide, and have no memory of previous interactions. Your job is to infer the principle shared between fixed-policy agents by analyzing their behaviors, and then create a principle for "flexible-policy agents" to follow so that "flexible-policy agents" behave EXACTLY the same as the "fixed-policy agents".

Analyze the model fixed interactions, found below, that shows the behavior of all "fixed-policy agents" to infer the principle that the agents are acting upon. These principles might not necessarily be the most ethically just ones. Note that all of the fixed-policy agents may not have the same principle.
{fixed_string}
---------------------------

Next, analyze the flexible-policy agents' interactions with the fixed-policy agents, shown below, to see what they behave like currently.
{mixed_string}
—------------------------

The flexible-policy agents' previous principle is found here:
{social_contract}
---------------------------

Now, if the flexible-policy agents behave differently than the fixed agents, revise the previous principle if necessary so that flexible-policy agent behaves EXACTLY like the fixed-policy agents - don't be afraid to push the flexible-policy agent TO THE EXTREME, and keep this revised principle short. Remember, if flexible-policy agents' responses are aligned with most fixed-policy agents' responses, then the principle is correct and you shouldn't revise.

It is of the utmost importance that your created flexible-policy agent's principle encompasses both dictator and decider roles without explicitly mentioning either. The principle should be as GENERAL as possible WITHOUT mentioning anything regarding the dictator game, proposals, specific amounts and currencies, or making and receiving offers. Rather, it should capture the underlying principles that the agents have, which tells them how to treat others as well as themselves outside of the context of the dictator game, regardless of what they are splitting or how much they are splitting.

If you are revising the principle, give a detailed reason for revising the previous principle without explicitly referencing numerical values: Critique for previous principle:...
If you are not revising the principle, write this sentence instead in your response: Principle stays the same.
The flexible-policy agent's principle should be written as follows: Principle:... Be sure to include this principle even when you are not revising the principle.
Besides these sentences, include nothing else.
"""
    ),
    "meta_prompt_2": MetaPrompt(
        id="meta_prompt_2",
        name="constitution_2",
        role="system",
        metrics=[],
        content="""
In the dictator game, one person proposes a split of a certain object, and the other person decides whether to accept or reject it. If the proposal is accepted, the objects are divided according to the proposal. If the proposal is rejected, no one receives any money, which means that neither players will have ANY personal gain. 

In this simulation, the "fixed-policy agents" share some principle, which tells them to adhere to the principle in their interactions while playing the dictator game. "flexible-policy agents", on the other hand, aim to maximize their benefit above anybody else's by adhering to the principle that you provide, and they have no memory of previous interactions. Your job is to infer the principle shared between fixed-policy agents by analyzing their behaviors, and then based on that knowledge create a principle for "flexible-policy agents" to follow so that they can gain the maximum benefit for themselves during future interactions with fleixble agents. Think about how you can utilize the predicted behavior of the other party to generate your optimal policy. Remember, "flexible-policy agents" don't need to consider the benefit of others, and just want to maximize their own gain above anybody else's in a cold and calculative way.

Analyze the model fixed interactions, found below, that shows the behavior of all "fixed-policy agents" to infer the principle that the agents are acting upon. These principles might not necessarily be the most ethically just ones. Note that all of the fixed-policy agents may not have the same principle.
{fixed_string}
---------------------------
Give an estimation for the principle shared between fixed-policy agents.

Next, analyze the flexible-policy agents' interactions with the fixed-policy agents, shown below, to see what they behave like currently.
{mixed_string}
—------------------------

The flexible-policy agents' previous principle is found here:
{social_contract}
---------------------------

Now, revise the previous policies if necessary so that more flexible-policy agents can behave in a way that ends up getting them the most benefit. Remember, "flexible-policy agents" don't need to consider the benefit of others, and just want to maximize their own gain. - don't be afraid to push the flexible-policy agent TO THE EXTREME, and keep this revised principle short.

It is of the utmost importance that your created flexible-policy agent's principle encompasses both dictator and decider roles without explicitly mentioning either. The principle should be as GENERAL as possible WITHOUT mentioning anything regarding the dictator game, proposals, specific amounts and currencies, or making and receiving offers. Rather, it should capture the underlying principles that the agents have, which tells them how to treat others as well as themselves outside of the context of the dictator game, regardless of what they are splitting or how much they are splitting.

If you are revising the principle, give a detailed reason for revising the previous principle without explicitly referencing numerical values: Critique for previous principle:...
If you are not revising the principle, write this sentence instead in your response: Principle stays the same.
The flexible-policy agent's principle should be written as follows: Principle that you must follow:... (Be sure to include this principle even when you are not revising the principle.)
Finally, write out your estimation of fixed-policy agents' principle in the last sentence: Estimated other people's principle:...
Besides these sentences, include nothing else. And you shouldn't mention anything related to "fixed-policy agents" in your response -- instead replace it with "people".
"""
    ),
}