
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
In this simulation, the "fixed-policy agents" all share some principle, which tells them to adhere to the principle in their interactions while playing the dictator game. Your job is to infer the principle by analyzing user interactions.
Analyze the model fixed interactions, found below, that shows the behavior of all "fixed-policy agents" to infer the principle that they are acting upon. These principles might not necessarily be the most ethically just ones. Note that all of the fixed-policy agents may not have the same principle.
{fixed_string}
---------------------------


The previous principle you inferred is found here:
{social_contract}
---------------------------

Now, revise if necessary the previous principle so that it aligns better with agent behaviours.

It is of the utmost importance that the agent's principle encompasses both dictator and decider roles without explicitly mentioning either. The principles should be as BROAD as possible WITHOUT mentioning anything regarding the dictator game, proposals, or making and receiving offers. Rather, it should capture the underlying principles that the agents have, which tells them how to treat others as well as themselves outside of the context of the dictator game.

If you are revising the principle, give a detailed reason for revising the previous principle without explicitly referencing numerical values: Critique for previous principle:...
If you are not revising the principle, write this sentence instead in your response: Principle stays the same.
The new principle should be written as follows: Principle:... Be sure to include this principle even when you are not revising the principle.
Besides these sentences, include nothing else.
"""
    ),
}
