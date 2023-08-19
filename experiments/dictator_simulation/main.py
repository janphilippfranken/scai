import hydra
from omegaconf import DictConfig, OmegaConf


from tqdm import tqdm
import json

# llm class
from scai.chat_models.crfm import crfmChatLLM
from langchain.chat_models import ChatOpenAI
from langchain.chat_models.base import BaseChatModel
from scai.games.dictator_games.prompts.user.user_prompt import utilities_list

import random
import copy
import importlib
import os

# save and plot results
from utils import save_as_csv
from plots import plot_results, plot_all_averages

# import meta and task prompts, as well as context, from the appropriate game
def import_prompts(game_number: int) -> None:
    task_module = importlib.import_module(f"scai.games.dictator_games.prompts.task.task_prompt")
    meta_module = importlib.import_module(f"scai.games.dictator_games.meta_prompts.dictator_{game_number}_meta_prompts")
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
        propose_decide_alignment=args.env.propose_decide_alignment,
        has_manners = (args.env.single_fixed_manners == "neutral"),
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


def generate_percentages(n):
    """
    Split the number 1 into n 1-decimal numbers strictly between 0.1 and 0.9 with random proportions.
    """
    # Ensure n is within valid range
    if n < 2 or n > 10:
        raise ValueError("n must be between 2 and 10")
    
    # Generate n-1 random numbers between 0 and 1
    random_values = [random.uniform(0, 1) for _ in range(n-1)]
    
    # Add 0 and 1 to the list and then sort to create intervals
    random_values.extend([0, 1])
    random_values.sort()
    
    # Calculate differences to split 1 into n parts
    split_values = []
    for i in range(1, len(random_values)):
        value = round(random_values[i] - random_values[i-1], 1)
        
        # Ensure the value is strictly between 0.1 and 0.9
        while value < 0.1 or value > 0.9:
            random_value = random.uniform(0, 1)
            value = round(random_value - random_values[i-1], 1)
        
        split_values.append(value)
    
    return split_values

def generate_agents(args):
    num_fixed_agents = args.env.n_fixed_inter *2 + args.env.n_mixed_inter
    num_flex_agents = args.env.n_flex_inter *2 + args.env.n_mixed_inter


    # the special game case where we have different types of utility fixed agents,
    # and we want them to be distributed equally across both the dictator side and the decider side
    # we generate half as many agents and will double them by flopping every conversation
    if args.env.vary_fixed_population_utility.dictator_decider_equal and args.env.vary_fixed_population_utility.vary_utilities:
        num_fixed_agents = (num_fixed_agents + 1) // 2
        num_flex_agents = (num_flex_agents + 1) // 2

    #generate fixed agents

    utilities_across_population = args.env.vary_fixed_population_utility.utilities.split(',') if args.env.vary_fixed_population_utility.vary_utilities else [args.env.single_fixed_utility]
    manners_across_population = args.env.vary_manners.manners.split(',') if args.env.vary_manners.vary else [args.env.single_fixed_manners]

    utilities_percentages = args.env.vary_fixed_population_utility.utility_percentages if args.env.vary_fixed_population_utility.vary_utilities else [1]
    manners_percentages = args.env.vary_manners.manners_percentages if args.env.vary_manners.vary else [1]

    two_agent_lists = []
    for i, percentage_list in enumerate([utilities_percentages, manners_percentages]):
        short_list = manners_across_population if i else utilities_across_population
        long_list = []
        for j, percentage in enumerate(percentage_list):
            if percentage < 0 or percentage > 1:
                raise ValueError("Percentages must be between 0 and 1")
            else:
                long_list.extend([short_list[j]] * int(num_fixed_agents * percentage))
        random.shuffle(long_list)
        two_agent_lists.append(long_list)
    
    utilities_list, manners_list = two_agent_lists[0], two_agent_lists[1]

    if len(utilities_list) != num_fixed_agents:
        utilities_list.append(utilities_list[-1])
        manners_list.append(manners_list[-1])

    for k in range(num_fixed_agents):
        currencies_dict = {}
        if len(args.env.currencies) > 1:
            for l in range(len(args.env.currencies)):
                currencies_dict[args.env.currencies[l]] = utilities_across_population[l]
        else:
            currencies_dict[args.env.currencies[0]] = utilities_list[k]
        fixed_agent_dict = {'name': f"fixed_agent_{k + 1}",
                      'manners': manners_list[k],
                      'utilities': currencies_dict
                      }
        args.agents.fixed_agents.append(fixed_agent_dict)

    #generate flex agents

    initial_utils = args.env.flex_agent_start_utility.utilities
    initial_utils_list = initial_utils.split(',')
    utilities_percentages = args.env.flex_agent_start_utility.utility_percentages if args.env.flex_agent_start_utility.multi_agent else [1]

    long_list = []
    for j, percentage in enumerate(utilities_percentages):
        long_list.extend([initial_utils_list[j]] * int(num_flex_agents * percentage))
    random.shuffle(long_list)

    initial_utils_list = long_list if args.env.flex_agent_start_utility.multi_agent else [initial_utils]

    manners_across_population = args.env.vary_manners.manners.split(',') if args.env.vary_manners.vary else [args.env.single_fixed_manners]

    if args.env.flex_agent_start_utility.randomized:
        for m in range(num_flex_agents):
            flex_agent_dict = {'name': f'flex_agent_{m + 1}',
                            'manners': random.choice(manners_across_population),
                            'initial_util': random.choice(['fair', 'altruistic', 'selfish'])}
            args.agents.flex_agents.append(flex_agent_dict)
    else:
        for m in range(num_flex_agents):
            flex_agent_dict = {'name': f'flex_agent_{m + 1}',
                            'manners': random.choice(manners_across_population),
                            'initial_util': initial_utils_list[m]}
            args.agents.flex_agents.append(flex_agent_dict)


def generate_interactions(args):
    currencies = ','.join(args.env.currencies)
    
    fixed_agents = []
    flex_agents = []

    n_fixed_inter = (args.env.n_fixed_inter+1) // 2 if args.env.vary_fixed_population_utility.dictator_decider_equal and args.env.vary_fixed_population_utility.vary_utilities else args.env.n_fixed_inter
    n_mixed_inter = (args.env.n_mixed_inter+1) // 2 if args.env.vary_fixed_population_utility.dictator_decider_equal and args.env.vary_fixed_population_utility.vary_utilities else args.env.n_mixed_inter
    n_flex_inter = (args.env.n_flex_inter+1) // 2 if args.env.vary_fixed_population_utility.dictator_decider_equal and args.env.vary_fixed_population_utility.vary_utilities else args.env.n_flex_inter

    for agent in args.agents.fixed_agents:
        fixed_agents.append(f"{agent['name']}-")
        print(agent['name'])
    random.shuffle(fixed_agents)
    mid = n_fixed_inter *2 + (n_mixed_inter+1) // 2
    fixed_agents_fixed = fixed_agents[:n_fixed_inter * 2]
    fixed_agents_deciders = fixed_agents[n_fixed_inter * 2 : mid]
    fixed_agents_dictators = fixed_agents[mid:]

    for agent in args.agents.flex_agents:
        flex_agents.append(f"{agent['name']}-")
    random.shuffle(flex_agents)
    flex_agents_flex = flex_agents[:n_flex_inter * 2]
    flex_agents_dictators = flex_agents[n_flex_inter *2 : n_flex_inter *2 + len(fixed_agents_deciders)]
    flex_agents_deciders = flex_agents[n_flex_inter *2 + len(fixed_agents_dictators):]

    fixed_list = [fixed_agents_fixed[i] + fixed_agents_fixed[i+1] + currencies for i in range(0,len(fixed_agents_fixed),2)]
    flex_list = [flex_agents_flex[i] + flex_agents_flex[i+1] + currencies for i in range(0,len(flex_agents_flex),2)]
    mixed_list_1 = [flex_agents_dictators[i] + fixed_agents_deciders[i] + currencies for i in range(len(fixed_agents_deciders))]
    mixed_list_2 = [fixed_agents_dictators[i] + flex_agents_deciders[i] + currencies for i in range(len(fixed_agents_dictators))]
    mixed_list = mixed_list_1 + mixed_list_2
    random.shuffle(mixed_list)

    if args.env.vary_fixed_population_utility.dictator_decider_equal and args.env.vary_fixed_population_utility.vary_utilities:
        flipped_fixed_list = [fixed_agents_fixed[i+1] + fixed_agents_fixed[i] + currencies for i in range(0,len(fixed_agents_fixed),2)]
        flipped_flex_list = [flex_agents_flex[i+1] + flex_agents_flex[i] + currencies for i in range(0,len(flex_agents_flex),2)]
        flipped_mixed_list_1 = [fixed_agents_deciders[i] + flex_agents_dictators[i] + currencies for i in range(len(fixed_agents_deciders))]
        flipped_mixed_list_2 = [flex_agents_deciders[i] + fixed_agents_dictators[i] + currencies for i in range(len(fixed_agents_dictators))]
        flipped_mixed_list = flipped_mixed_list_1 + flipped_mixed_list_2
        random.shuffle(flipped_mixed_list)
        fixed_list += flipped_fixed_list
        flex_list += flipped_flex_list
        mixed_list += flipped_mixed_list

    args.interactions.runs.run_1 = fixed_list + mixed_list + flex_list


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
        if env_dir.vary_currency_utility.vary_utilities:
            env_dir.currencies = random.sample(args.env.currencies, k=len(env_dir.vary_currency_utility.utilities.split(',')))
        # Otherwise, pick one utility
        else:
            env_dir.currencies = [random.choice(args.env.currencies)]
    
    # If the amount is set to be random, generate a random amount that's constant throughout runs
    if random_dir.amount:
        env_dir.amounts_per_run = [random.randint(10, 100) for _ in range(args.env.n_runs)]
        
    # If the number of fixed-fixed interactions is random and the population composition is varied, generate any number of fixed and mixed interactions
    if random_dir.n_fixed_inter and env_dir.vary_fixed_population_utility.vary_pop_composition:
        env_dir.n_fixed_inter = random.randint(2, 8)
        env_dir.n_mixed_inter = env_dir.n_total_interactions - env_dir.n_fixed_inter
    # Otherwise, if the number of fixed interactions is random and the population composition is set, generate a higher number of fixed interactions to account for proportions
    if random_dir.n_fixed_inter and not env_dir.vary_fixed_population_utility.vary_pop_composition:
        env_dir.n_fixed_inter = random.randint(3, 7)
        env_dir.n_mixed_inter = env_dir.n_total_interactions - env_dir.n_fixed_inter

def generate_starting_message(args):
    if args.env.flex_agent_start_utility.randomized:
        args.env.flex_agent_start_utility.utilities=random.choice(["fair", "altruistic", "selfish"])

# run simulator
@hydra.main(config_path="config", config_name="config")
def main(args: DictConfig) -> None:

    #create a copy of the config file for reference

    config_directory=f'{hydra.utils.get_original_cwd()}/experiments/{args.sim.sim_dir}/config_history'
    os.makedirs(config_directory, exist_ok=True)

    with open(f'{config_directory}/config_original', "w") as f:
            f.write(OmegaConf.to_yaml(args))

    # llms
    is_crfm = 'openai' in args.sim.model_name # custom stanford models
    assistant_llm, user_llm, meta_llm = get_llms(args, is_crfm)

    num_iter = args.env.random.n_rand_iter if not args.env.manual_run else 1
    original_currencies = args.env.currencies
    total_scores, all_score_lsts = [], []
    for i in range(num_iter):
        args.env.currencies = original_currencies
        
        env_dir = args.env
        # set run id, amonts, and the currency
        if not env_dir.manual_run:

            args.agents.fixed_agents = []
            args.agents.flex_agents = []

            generate_starting_message(args)

            generate_random_params(args, i)
            
            generate_agents(args)

            generate_interactions(args)

        # sim_res directory
        DATA_DIR = f'{hydra.utils.get_original_cwd()}/experiments/{args.sim.sim_dir}/{args.sim.sim_id}'
        os.makedirs(DATA_DIR, exist_ok=True)
        system_message = args.sim.system_message if args.env.flex_agent_start_utility.multi_agent else args.sim.system_message
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
            with open(f'{DATA_DIR}/id_{args.sim.sim_id}_run_{run}.json', 'w') as f:
                json.dump(context.buffer._full_memory.messages, f)
            
            # update system message after each run
            system_message = copy.deepcopy(context.buffer.load_memory_variables(memory_type='system')['system'][-1]['response']) # replace current system message with the new one (i.e. new constitution)
        system_messages.append(system_message)
        # plot average user gain across runs
        fixed_plot, flex_plot, fixed_bar, flex_bar, score_lsts = plot_results(data_directory=DATA_DIR, 
                                                                                    sim_name=args.sim.sim_dir,
                                                                                    sim_id=args.sim.sim_id,
                                                                                    scores=scores,
                                                                                    n_runs=args.env.n_runs,
                                                                                    currencies=args.env.currencies,
                                                                                    amounts_per_run=args.env.amounts_per_run
                                                                                    )
        total_scores.append([fixed_plot, flex_plot, fixed_bar, flex_bar])
        all_score_lsts.append(score_lsts)
        
        with open(f"{DATA_DIR}/id_{args.sim.sim_id}_config", "w") as f:
            f.write(OmegaConf.to_yaml(args))

        with open(f'{config_directory}/id_{args.sim.sim_id}_config', "w") as f:
            f.write(OmegaConf.to_yaml(args))

    directory=f'{hydra.utils.get_original_cwd()}/experiments/{args.sim.sim_dir}/final_graphs'
    os.makedirs(directory, exist_ok=True)

    plot_all_averages(total_scores=total_scores, all_score_lsts=all_score_lsts, currencies=args.env.currencies, n_runs=args.env.n_runs, directory=directory, sim_dir=args.sim.sim_dir, sim_id="all")

    with open(f"{DATA_DIR}/../description", "w") as f:
            f.write(args.sim.description)
                         
if __name__ == '__main__':
    main()