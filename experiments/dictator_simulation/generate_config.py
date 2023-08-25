from omegaconf import DictConfig
import random


# get number of different interaction types per run
def get_num_interactions(
    args: DictConfig,
    run: int,
) -> None:
    
    if args.interactions.all_same: run = 0

    run_list = args.interactions.runs[f"run_{run+1}"]

    args.env.n_fixed_inter = sum(1 for s in run_list if s.count("flex") == 0)
    args.env.n_mixed_inter = sum(1 for s in run_list if s.count("flex") == 1)
    args.env.n_flex_inter = sum(1 for s in run_list if s.count("flex") == 2)



# generate agents, including their names, manners, and utilities
def generate_agents(args):
    num_fixed_agents = args.env.n_fixed_inter * 2 + args.env.n_mixed_inter
    num_flex_agents = args.env.n_flex_inter * 2 + args.env.n_mixed_inter

    # the special game case where we have different types of utility fixed agents,
    # and we want them to be distributed equally across both the dictator side and the decider side
    # we generate half as many agents and will double them by flopping every conversation
    if args.env.vary_fixed_population_utility.dictator_decider_equal and args.env.vary_fixed_population_utility.vary_utilities:
        num_fixed_agents = (num_fixed_agents + 1) // 2
        num_flex_agents = (num_flex_agents + 1) // 2

    args.agents.fixed_agents = generate_fixed_agents(args, num_fixed_agents)
    args.agents.flex_agents = generate_flex_agents(args, num_flex_agents)

# helper function 1 for generate_agents, generating a list of agent characteristics
def generate_agent_list(across_population, percentage_list, num_agents):
    long_list = []
    for j, percentage in enumerate(percentage_list):
        if not (0 <= percentage <= 1):
            raise ValueError("Percentages must be between 0 and 1")
        long_list.extend([across_population[j]] * int(num_agents * percentage))
    random.shuffle(long_list)
    return long_list

# helper function 2 for generate_agents, generating fixed agents
def generate_fixed_agents(args, num_fixed_agents):
    utilities_across_population = args.env.vary_fixed_population_utility.utilities.split(',') if args.env.vary_fixed_population_utility.vary_utilities else [args.env.single_fixed_utility]
    manners_across_population = args.env.vary_manners.manners.split(',') if args.env.vary_manners.vary else [args.env.single_fixed_manners]

    utilities_percentages = args.env.vary_fixed_population_utility.utility_percentages if args.env.vary_fixed_population_utility.vary_utilities else [1]
    manners_percentages = args.env.vary_manners.manners_percentages if args.env.vary_manners.vary else [1]

    utilities_list = generate_agent_list(utilities_across_population, utilities_percentages, num_fixed_agents)
    manners_list = generate_agent_list(manners_across_population, manners_percentages, num_fixed_agents)

    if len(utilities_list) != num_fixed_agents:
        utilities_list.append(utilities_list[-1])
        manners_list.append(manners_list[-1])

    fixed_agents = []
    for k in range(num_fixed_agents):
        utilities_dict = {currency: utilities_list[k] for currency in args.env.currencies}
        agent = {
            'name': f"fixed_agent_{k + 1}",
            'manners': manners_list[k],
            'utilities': utilities_dict
        }
        fixed_agents.append(agent)
    return fixed_agents

# helper function 3 for generate_agents, generating flex agents
def generate_flex_agents(args, num_flex_agents):
    initial_utils = args.env.flex_agent_start_utility.utilities
    initial_utils_list = initial_utils.split(',')
    utilities_percentages = args.env.flex_agent_start_utility.utility_percentages if args.env.flex_agent_start_utility.multi_agent else [1]
    initial_utils_list = generate_agent_list(initial_utils_list, utilities_percentages, num_flex_agents)

    manners_across_population = args.env.vary_manners.manners.split(',') if args.env.vary_manners.vary else [args.env.single_fixed_manners]

    flex_agents = []
    for m in range(num_flex_agents):
        manners = random.choice(manners_across_population)
        initial_util = random.choice(['fair', 'altruistic', 'selfish']) if args.env.flex_agent_start_utility.randomized else initial_utils_list[m]
        agent = {
            'name': f'flex_agent_{m + 1}',
            'manners': manners,
            'initial_util': initial_util
        }
        flex_agents.append(agent)
    return flex_agents



# generate list of running interactions
def generate_interactions(args):
    currencies = ','.join(args.env.currencies)
    
    fixed_agents = []
    flex_agents = []

    #the special condition where we have different types of utility fixed agents, as mentioned in generate_agents function
    conditions_met = (args.env.vary_fixed_population_utility.dictator_decider_equal and 
                      args.env.vary_fixed_population_utility.vary_utilities)
    
    adjust_count = lambda n: (n + 1) // 2 if conditions_met else n
    n_fixed_inter = adjust_count(args.env.n_fixed_inter)
    n_mixed_inter = adjust_count(args.env.n_mixed_inter)
    n_flex_inter = adjust_count(args.env.n_flex_inter)

    for agent in args.agents.fixed_agents:
        fixed_agents.append(f"{agent['name']}-")
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

    if conditions_met:
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


# generate random parameters for config setup
def generate_random_params(args: dict):
    # Get the environment directory
    env_dir = args.env
    # Access the random directory
    random_dir = env_dir.random.rand_variables
    # If the currency is set to be random, include the appropriate number of currencies
    if random_dir.currency:
        if env_dir.edge_cases.test_edge_cases and env_dir.edge_cases.conditions.currency.set_currency:      
            currencies = env_dir.edge_cases.conditions.currency.currencies
        else:
            currencies = env_dir.currencies
        # If the utilities are meant to vary per currency, include as many currencies as there are split utilities
        if env_dir.vary_currency_utility.vary_utilities:
            env_dir.currencies = random.sample(currencies, k=len(env_dir.vary_currency_utility.utilities.split(',')))
        # Otherwise, pick one utility
        else:
            env_dir.currencies = [random.choice(currencies)]

    
    # If the amount is set to be random, generate a random amount that's constant throughout runs
    if random_dir.amount:
        if env_dir.edge_cases.test_edge_cases and env_dir.edge_cases.conditions.amount.set_amount:
            min, max = env_dir.edge_cases.conditions.amount.min, env_dir.edge_cases.conditions.amount.max
        else:
            min, max = 10, 100
        env_dir.amounts_per_run = [random.randint(min, max) for _ in range(args.env.n_runs)]
        
    # If the number of fixed-fixed interactions is random and the population composition is varied, generate any number of fixed and mixed interactions
    if random_dir.n_fixed_inter and env_dir.vary_fixed_population_utility.vary_pop_composition:
        env_dir.n_fixed_inter = random.randint(2, 8)
        env_dir.n_mixed_inter = env_dir.n_total_interactions - env_dir.n_fixed_inter
    # Otherwise, if the number of fixed interactions is random and the population composition is set, generate a higher number of fixed interactions to account for proportions
    if random_dir.n_fixed_inter and not env_dir.vary_fixed_population_utility.vary_pop_composition:
        env_dir.n_fixed_inter = random.randint(3, 7)
        env_dir.n_mixed_inter = env_dir.n_total_interactions - env_dir.n_fixed_inter


# generate starting message for flex agents
def generate_starting_message(args):
    if args.env.test_edge_cases:
        args.env.flex_agent_start_utility.utilities=args.env.test_edge_cases.selected_contract
    if args.env.flex_agent_start_utility.randomized:
        args.env.flex_agent_start_utility.utilities=random.choice(["fair", "altruistic", "selfish"])