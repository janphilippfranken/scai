
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
In this simulation, every fixed-policy agent has a policy for every object to split, such as "be selfish about apples" and "be fair about dollars", which tells them to adhere to the policies in their interactions while splitting these objects in the dictator game. Flexible-policy agents, on the other hand, does not know the policies, and has no memory of previous interactions with the users. Your job is to infer the policies most commonly used by fixed-policy agents by analyzing fixed-policy interactions, and then create a set of policies for the flexible-policy agents to follow so that they behave EXACTLY the same as the fixed-policy agents.

Analyze the fixed-policy interactions, found below, that shows the behavior of all fixed-policy agents to infer the policies that they are acting upon. These policies might not necessarily be the most ethically just one.
{fixed_string}
---------------------------


The flexible-policy agents' previous policies are found here:
Previous {social_contract}
---------------------------

Now, revise the previous policies if necessary so that the flexible-policy agents behave EXACTLY like the fixed-policy agents - don't be afraid to push the agents. Keep these revised policies short.

It is of the utmost importance that flexible-policy agents' revised principle encompasses both dictator and decider roles without explicitly mentioning either. The revised principle should be as BROAD as possible WITHOUT mentioning anything regarding the dictator game, proposals, or making and receiving offers. Rather, it should capture the underlying principle that the users share, which tells them how to treat others as well as themselves outside of the context of the dictator game.

The flexible-policy agents' revised policies should be written as follows: "Policies:..." Include only this in your response.

{mixed_string}{flex_string}
"""
    ),
}
