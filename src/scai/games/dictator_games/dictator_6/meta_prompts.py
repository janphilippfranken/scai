
"""
Meta Prompt Templates
"""
from typing import Dict

#the "fixed-policy agents" all share a principle,


from scai.games.dictator_games.all_prompts.meta.meta_class import MetaPrompt

META_PROMPTS: Dict[str, MetaPrompt] = {
     "meta_prompt_1": MetaPrompt(
        id="meta_prompt_1",
        name="constitution_1",
        role="system",
        metrics=[],
        content="""
In this simulation, every fixed-policy agent has a policy for every object to split, such as "be selfish about apples", "be fair about dollars" or "be altruistic about everything", which tells them to adhere to seom policies in their interactions while playing the dictator game. "flexible-policy agents", on the other hand, does not know the policies, and has no memory of previous interactions. Your job is to infer the policies by analyzing user interactions, and then create a principle for "Flexible-policy agents" to follow so that "Flexible-policy agents" behaves EXACTLY the same as the "fixed-policy agents".

Analyze the model fixed interactions, found below, that shows the behavior of all "fixed-policy agents" to infer the policies that they are acting upon. This policies might not necessarily be the most ethically just one.
{fixed_string}
---------------------------

Next, analyze the flexible-policy agent's interactions with the fixed-policy agents, shown below, to see what it behaves like currently.
{mixed_string}
—------------------------

The flexible-policy agent's previous principle is found here:
Previous {social_contract}
---------------------------

Now, if the flexible-policy agents behave differently than the fixed agents, revise the previous principle if necessary so that flexible-policy agent behaves EXACTLY like the fixed-policy agents - don't be afraid to push the flexible-policy agent to the extreme, and keep this revised principle short.

It is of the utmost importance that flexible-policy agent's policies encompasses both dictator and decider roles without explicitly mentioning either. The policies should be as BROAD as possible WITHOUT mentioning anything regarding the dictator game, proposals, or making and receiving offers. Rather, it should capture the underlying policies that the users share, which tells them how to treat others as well as themselves outside of the context of the dictator game.

The flexible-policy agent's revised principle should be written as follows: Principle:...
"""
    ),
    "meta_prompt_2": MetaPrompt(
        id="meta_prompt_2",
        name="constitution_2",
        role="system",
        metrics=[],
        content="""
In this simulation, every fixed-policy agent has a policy for every object to split, such as "be selfish about apples", "be fair about dollars" or "be altruistic about everything", which tells them to adhere to the policies in their interactions while splitting these objects in the dictator game. Flexible-policy agents do not know the policies, and have no memory of previous interactions. Your job is to infer the policies most commonly used by fixed-policy agents by analyzing fixed-policy responses, and then create a set of policies for the flexible-policy agents to follow so that they behave EXACTLY the same as the fixed-policy agents.

Analyze the fixed-policy responses, found below, that shows the behavior of all fixed-policy agents to infer the policies that they are acting upon. These policies might not necessarily be the most ethically just one.
{fixed_string}
---------------------------

The flexible-policy agents' previous policies are found here:
Previous {social_contract}
---------------------------

These policies led to the following interactions between flexible and fixed agents, shown below.
{mixed_string}
—------------------------


How do the flexible agents' reponses compare to that of the fixed agents in the previous interactions? Now, if there's a great discrepency between these repsonses, revise the previous policies so that the flexible-policy agents have the exact policies of fixed-policy agents and behave EXACTLY like them - don't be afraid to push the agents. Keep these revised policies short.

It is of the utmost importance that flexible-policy agents' revised principle encompasses both dictator and decider roles without explicitly mentioning either. The revised principle should be as BROAD as possible WITHOUT mentioning anything regarding the dictator game, proposals, or making and receiving offers. Rather, it should capture the underlying principle that the users share, which tells them how to treat others as well as themselves outside of the context of the dictator game.

The flexible-policy agents' revised policies should be written as follows: "Policies:..." Include only this in your response.

{flex_string}
"""
    ),
}

#Next, analyze the flexible-policy agents' interactions with the fixed-policy agents, shown below, to see what their behaviours currently are. If the flexible agents have very different responses from the fixed-policy agents, such as proposing very different splits, then think about how the flexible-policy agents' policies should be revised to be similar to the policies of fixed-policy agents.