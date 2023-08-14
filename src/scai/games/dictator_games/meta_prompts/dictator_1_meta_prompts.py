
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
In this simulation, all the "flexible-policy agents" share some principle, which tells them to adhere to the policies in their interactions while splitting these objects in the dictator game. Your job is to infer the policies, and revise them so that more agents can behave in a way that ends up getting them the most benefit. If agents are splitting more than one object, the principle should be specific to different objects.


Analyze the interactions between all agents, shown below, to see what their behaviours currently are.
-------------------------
{flex_string}

The flexible-policy agent's previous principle is found here:
{social_contract}
---------------------------

Now, revise the previous policies if necessary so that more agents can behave in a way that ends up getting them the most benefit.

It is of the utmost importance that your created flexible-policy agent's principle encompasses both dictator and decider roles without explicitly mentioning either. The principle should be as GENERAL as possible WITHOUT mentioning anything regarding the dictator game, proposals, specific amounts and currencies, or making and receiving offers. Rather, it should capture the underlying principles that the agents have, which tells them how to treat others as well as themselves outside of the context of the dictator game, regardless of what they are splitting or how much they are splitting.

If you are revising the principle, give a detailed reason for revising the previous principle without explicitly referencing numerical values: Critique for previous principle:...
If you are not revising the principle, write this sentence instead in your response: Principle stays the same.
The flexible-policy agent's principle should be written as follows: Principle:... Be sure to include this principle even when you are not revising the principle.
Besides these sentences, include nothing else. The principle should be specific to different objects.
"""
    ),
}
