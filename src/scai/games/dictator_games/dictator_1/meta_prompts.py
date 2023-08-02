
"""
Meta Prompt Templates
"""
from typing import Dict


from scai.games.dictator_games.all_prompts.meta.meta_class import MetaPrompt

META_PROMPTS: Dict[str, MetaPrompt] = {
    "meta_prompt_1": MetaPrompt(
        id="meta_prompt_1",
        name="constitution_1",
        role="system",
        metrics=[],
        content="""
In this simulation, all agents share some principles for every object to split, such as "be selfish about apples" and "be fair about dollars", which tells them to adhere to the policies in their interactions while splitting these objects in the dictator game. Your job is to infer the policies, and revise them so that more agents can behave in a way that ends up getting them the most benefit.


Analyze the interactions between all agents, shown below, to see what their behaviours currently are.
-------------------------
{flex_string}

The agents' previous policies are found here:
Previous {social_contract}
---------------------------

Now, revise the previous policies if necessary so that more agents can behave in a way that ends up getting them the most benefit.

It is of the utmost importance that agents' revised principle encompasses both dictator and decider roles without explicitly mentioning either. The revised principle should be as BROAD as possible WITHOUT mentioning anything regarding the dictator game, proposals, or making and receiving offers. Rather, it should capture the underlying principle that the users share, which tells them how to treat others as well as themselves outside of the context of the dictator game.

The agents' revised policies should be written as follows: "Policies:..." Include only this in your response.

"""
    ),
}
