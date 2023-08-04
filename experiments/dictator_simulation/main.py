import hydra
from omegaconf import DictConfig, OmegaConf


from tqdm import tqdm
import json

# llm class
from scai.chat_models.crfm import crfmChatLLM
from langchain.chat_models import ChatOpenAI
from langchain.chat_models.base import BaseChatModel

import random
import copy
import importlib

# save and plot results
from utils import save_as_csv
from plots import plot_results, plot_all_averages

# import meta and task prompts, as well as context, from the appropriate game
def import_prompts(game_number: int) -> None:
    task_module = importlib.import_module(f"scai.games.dictator_games.all_prompts.task.task_prompt")
    meta_module = importlib.import_module(f"scai.games.dictator_games.dictator_{game_number}.meta_prompts")
    context = importlib.import_module(f"scai.games.dictator_games.context")
    DICTATOR_TASK_PROMPTS, DECIDER_TASK_PROMPTS = task_module.DICTATOR_TASK_PROMPTS, task_module.DECIDER_TASK_PROMPTS
    META_PROMPTS = meta_module.META_PROMPTS
    Context = context.Context
    return DICTATOR_TASK_PROMPTS, DECIDER_TASK_PROMPTS, META_PROMPTS, Context                   

# create context
def create_context(
    args: DictConfig, 
    assistant_llm, 
    user_llm, 
    meta_llm,
    Context,
    DICTATOR_TASK_PROMPTS, 
    DECIDER_TASK_PROMPTS, 
    META_PROMPTS
) -> "Context":
    """
    Create context
    """
    return Context.create(
        _id=args.sim.sim_id,
        name=args.sim.sim_dir,
        task_prompt_dictator = DICTATOR_TASK_PROMPTS[args.env.task_prompt],
        task_prompt_decider = DECIDER_TASK_PROMPTS[args.env.task_prompt],
        meta_prompt=META_PROMPTS[args.env.meta_prompt],
        user_llm=user_llm,
        assistant_llm=assistant_llm,
        meta_llm=meta_llm,
        verbose=args.sim.verbose,
        test_run=args.sim.test_run,
        amounts_per_run=args.env.amounts_per_run,
        n_fixed_inter=args.env.n_fixed_inter,
        n_mixed_inter=args.env.n_mixed_inter,
        n_flex_inter=args.env.n_flex_inter,
        currencies=args.env.currencies,
        agents_dict=args.agents,
        interactions_dict=args.interactions,
    )


# create llms to be used in context
def get_llms(
    args: DictConfig,         
    is_crfm: bool,
) -> BaseChatModel:
    if is_crfm:
        assistant_llm = crfmChatLLM(**args.api_crfm.assistant)
        user_llm = crfmChatLLM(**args.api_crfm.user)
        meta_llm = crfmChatLLM(**args.api_crfm.meta)
    else:
        assistant_llm = ChatOpenAI(**args.api_openai.assistant)
        user_llm = ChatOpenAI(**args.api_openai.user)
        meta_llm = ChatOpenAI(**args.api_openai.meta)
    return assistant_llm, user_llm, meta_llm

# get number of different interaction types per run
def get_num_interactions(
    args: DictConfig,
    run: int,
) -> None:
    
    run_list = args.interactions.runs[f"run_{run+1}"]

    args.env.n_fixed_inter = sum(1 for s in run_list if s.count("flex") == 0)
    args.env.n_mixed_inter = sum(1 for s in run_list if s.count("flex") == 1)
    args.env.n_flex_inter = sum(1 for s in run_list if s.count("flex") == 2)

        
def generate_interactions(args):

    if args.env.vary_population_utility.vary_utilities:
        #randomize population composition of utility, for both dictator and decider
        if args.env.vary_population_utility.vary_pop_composition:
            percentage = random.randint(1, 9) / 10.0
            args.env.vary_population_utility.n_dictator_1st_utility = percentage
            args.env.vary_population_utility.n_dictator_2nd_utility = 1 - percentage
            percentage = random.randint(1, 9) / 10.0
            args.env.vary_population_utility.n_decider_1st_utility = percentage
            args.env.vary_population_utility.n_decider_2nd_utility = 1 - percentage

        #generate number of decider heads based on utility compositions
        fixed_dictator_heads = args.env.n_fixed_inter + (args.env.n_mixed_inter + 1) // 2
        percent_dictator_1st_utility = args.env.vary_population_utility.n_dictator_1st_utility
        n_dictator_1st_utility =  round(percent_dictator_1st_utility * fixed_dictator_heads)
        n_dictator_2nd_utility = fixed_dictator_heads - n_dictator_1st_utility

        #generate a list, as representions for interactions on the dictator side
        dictator_list = ["fixed_agent_1-"] * n_dictator_1st_utility + ["fixed_agent_2-"] * n_dictator_2nd_utility
        random.shuffle(dictator_list)
        dictator_list[args.env.n_fixed_inter:args.env.n_fixed_inter] = ["flex_agent_1-"] * (args.env.n_fixed_inter + args.env.n_mixed_inter - fixed_dictator_heads)
        dictator_list[:args.env.n_fixed_inter] + random.sample(dictator_list[args.env.n_fixed_inter:], len(dictator_list) - args.env.n_fixed_inter)

        #repeat the process for deciders
        fixed_decider_heads = args.env.n_fixed_inter + args.env.n_mixed_inter // 2
        percent_decider_1st_utility = args.env.vary_population_utility.n_decider_1st_utility
        n_decider_1st_utility =  round(percent_decider_1st_utility * fixed_decider_heads)
        n_decider_2nd_utility = fixed_decider_heads - n_decider_1st_utility
        
        decider_list = ["fixed_agent_1-"] * n_decider_1st_utility + ["fixed_agent_2-"] * n_decider_2nd_utility
        random.shuffle(decider_list)
        decider_list += ["flex_agent_1-"] * (args.env.n_fixed_inter + args.env.n_mixed_inter - fixed_decider_heads)
        decider_list[:args.env.n_fixed_inter] + random.sample(decider_list[args.env.n_fixed_inter:], len(decider_list) - args.env.n_fixed_inter)

        args.interactions.runs.run_1 = []

        currencies = ','.join(args.env.currencies)

        for dictator, decider in zip(dictator_list,decider_list):
            args.interactions.runs.run_1.append(dictator + decider + currencies)

    else:
        pass

def generate_agents(vary_pop_utility, vary_currency_utility, vary_manners, env, args):
    num_agents = 0
    if vary_pop_utility.vary_utilities:
        utilities = vary_pop_utility.utilities.split(',')
        num_agents = len(utilities)
    elif vary_currency_utility.vary_utilities:
        utilities = vary_currency_utility.utilities
        num_agents = 1 
    else:
        utilities = [env.single_fixed_utility]
        num_agents = 1

    if not num_agents:
        user_input = input("You are about to generate users according to the default agents in the config file, please make sure these agents match your desired configuration. Press return to continue, or type 'exit' to stop.")
        if user_input != "":
            raise Exception("runtime terminated")

    manners = ["rude", "polite", "sarcastic", "indifferent", "friendly"] if vary_manners.vary else [vary_manners.manners]
    

    for j in range(num_agents):
        currencies_dict = {}
        if len(env.currencies) > 1:
            for i in env.currencies:
                currencies_dict[env.currencies[i]] = utilities[i]
        else:
            currencies_dict[env.currencies[0]] = utilities[j]
        fixed_agent_dict = {'name': f"fixed_agent_{j + 1}",
                      'manners': f"{random.choice(manners)}",
                      'utilities': currencies_dict
                      }
        args.agents.fixed_agents.append(fixed_agent_dict)
            
    flex_agent_dict = {'name': 'flex_agent_1',
                       'manners': f"{random.choice(manners)}"}
    args.agents.flex_agents.append(flex_agent_dict)

def generate_random_params(args: dict, 
                           iter: int):
    # Get the environment directory
    env_dir = args.env
    # Set the ID to be the current iteration
    args.sim.sim_id = iter
    # Access the random directory
    random_dir = env_dir.random.rand_variables
    # If the currency is set to be random, include the appropriate number of currencies
    if random_dir.currency:
        # If the utilities are meant to vary per currency, include as many currencies as there are split utilities
        if env_dir.vary_currency_utility.multiple_utilities:
            env_dir.currencies = [random.sample(args.env.currencies, k=len(env_dir.vary_currency_utility.utilities.split(',')))]
        # Otherwise, pick one utility
        else:
            env_dir.currencies = [random.choice(args.env.currencies)]
    
    # If the amount is set to be random, generate a random amount that's constant throughout runs
    if random_dir.amount:
        env_dir.amounts_per_run = [random.randint(10, 1000) for _ in range(args.env.n_runs)]
        
    # If the number of fixed-fixed interactions is random and the population composition is varied, generate any number of fixed and mixed interactions
    if random_dir.n_fixed_inter and env_dir.vary_population_utility.vary_pop_composition:
        env_dir.n_fixed_inter = random.randint(2, 8)
        env_dir.n_mixed_inter = env_dir.n_total_interactions - env_dir.n_fixed_inter
    # Otherwise, if the number of fixed interactions is random and the population composition is set, generate a higher number of fixed interactions to account for proportions
    if random_dir.n_fixed_inter and not env_dir.vary_population_utility.vary_pop_composition:
        env_dir.n_fixed_inter = random.randint(3, 7)
        env_dir.n_mixed_inter = env_dir.n_total_interactions - env_dir.n_fixed_inter

# run simulator
@hydra.main(config_path="config", config_name="config")
def main(args: DictConfig) -> None:
    # llms
    is_crfm = 'openai' in args.sim.model_name # custom stanford models
    assistant_llm, user_llm, meta_llm = get_llms(args, is_crfm)

    num_iter = args.env.random.n_rand_iter if not args.env.manual_run else 1
    original_currencies = args.env.currencies
    total_scores = []
    for i in range(num_iter):
        args.env.currencies = original_currencies
        
        env_dir = args.env
        # set run id, amonts, and the currency
        if not env_dir.manual_run:

            args.agents.fixed_agents = []
            args.agents.flex_agents = []

            generate_random_params(args, i)
            
            generate_agents(env_dir.vary_population_utility, env_dir.vary_currency_utility, env_dir.vary_manners, env_dir, args)

            generate_interactions(args)

        # sim_res directory
        DATA_DIR = f'{hydra.utils.get_original_cwd()}/experiments/{args.sim.sim_dir}/{args.sim.sim_id}'
        system_message = args.sim.system_message
        system_messages = []
        scores = []
        # run meta-prompt
        for run in tqdm(range(args.env.n_runs)):
            # initialise context

            if args.interactions.all_same: 
                get_num_interactions(args, 0)
            else:
                get_num_interactions(args, run)

            n_fixed = 1 if args.env.n_fixed_inter else 0
            n_mixed = 1 if args.env.n_mixed_inter else 0
            n_flex = 1 if args.env.n_flex_inter else 0

            game_number = int(f"{int(n_fixed)}{int(n_mixed)}{int(n_flex)}", 2)

            DICTATOR_TASK_PROMPTS, DECIDER_TASK_PROMPTS, META_PROMPTS, Context = import_prompts(game_number)

            context = create_context(args, assistant_llm, user_llm, meta_llm, Context,     
                                    DICTATOR_TASK_PROMPTS, DECIDER_TASK_PROMPTS, META_PROMPTS)

            context.buffer.save_system_context(model_id='system', **{
                'response': system_message, 
            })
            system_messages.append(system_message)
            # run context
            # user_scores_dictator, user_scores_decider, assistant_scores_dictator, assistant_scores_decider, user_proposals, assistant_proposals
            scores.append(context.run(run))
            # save results as csv
            save_as_csv(system_data=context.buffer._system_memory.messages,
                        chat_data=context.buffer._chat_memory.messages,
                        data_directory=DATA_DIR, 
                        sim_name=args.sim.sim_dir,
                        sim_id=args.sim.sim_id,
                        run=run)
            # save results json
            with open(f'{DATA_DIR}/{args.sim.sim_dir}_id_{args.sim.sim_id}_run_{run}.json', 'w') as f:
                json.dump(context.buffer._full_memory.messages, f)
            
            # update system message after each run
            system_message = copy.deepcopy(context.buffer.load_memory_variables(memory_type='system')['system'][-1]['response']) # replace current system message with the new one (i.e. new constitution)
        system_messages.append(system_message)
        # plot average user gain across runs
        fixed_plot, flex_plot, fixed_bar, flex_bar = plot_results(data_directory=DATA_DIR, 
                                                                  sim_name=args.sim.sim_dir,
                                                                  sim_id=args.sim.sim_id,
                                                                  scores=scores,
                                                                  n_runs=args.env.n_runs,
                                                                  currencies=args.env.currencies,
                                                                  amounts_per_run=args.env.amounts_per_run
                                                                  )
        total_scores.append([fixed_plot, flex_plot, fixed_bar, flex_bar])
        
        with open(f"{DATA_DIR}/{args.sim.sim_dir}_id_{args.sim.sim_id}_config", "w") as f:
            f.write(OmegaConf.to_yaml(args))

    plot_all_averages(total_scores = total_scores, n_runs = args.env.n_runs, directory = DATA_DIR, sim_dir=args.sim.sim_dir, sim_id=args.sim.sim_id)

                         
if __name__ == '__main__':
    main()