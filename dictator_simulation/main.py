import copy
import importlib
import os
import json
import hydra
from tqdm import tqdm
from omegaconf import DictConfig, OmegaConf
import random
from typing import List
# llm class
from gpt4 import GPT4Agent
from azure import AsyncAzureChatLLM

"""
from scai.chat_models.crfm import crfmChatLLM
from langchain.chat_models import ChatOpenAI
from langchain.chat_models.base import BaseChatModel
"""

# set up context
from scai.dictator_games.context import Context
from scai.dictator_games.prompts.task.task_prompt import DICTATOR_TASK_PROMPTS, DECIDER_TASK_PROMPTS   
from generate_config import get_num_interactions, generate_agents, generate_interactions, generate_random_params, generate_starting_message

# save and plot results
from utils import save_as_csv
from plots import plot_results, plot_all_averages, plot_questions
from generalize_utils import create_prompt_string, set_args, set_args_2, reset_args_2, get_existing_data

# create context
def create_context(
    static_args: DictConfig, 
    variable_args: List[DictConfig],
    assistant_llm, 
    user_llm, 
    meta_llm,
    oracle_llm,
    Context,
    DICTATOR_TASK_PROMPTS, 
    DECIDER_TASK_PROMPTS, 
    META_PROMPTS
) -> "Context":
    """
    Create context
    """
    ids, amounts, currencies, agents = [], [], [], []
    for args in variable_args:
        ids.append(args.sim.sim_id)
        amounts.append(args.env.amounts_per_run)
        currencies.append(args.env.currencies)
        agents.append(args.agents)
        
    return Context.create(
        _id=ids, # VARIABLE ARGUMENT
        name=static_args.sim.sim_dir, #  the directory will be the same regardless
        task_prompt_dictator = DICTATOR_TASK_PROMPTS[static_args.env.task_prompt],
        task_prompt_decider = DECIDER_TASK_PROMPTS[static_args.env.task_prompt],
        meta_prompt=META_PROMPTS[static_args.env.meta_prompt],
        user_llm=user_llm,
        assistant_llm=assistant_llm,
        meta_llm=meta_llm,
        oracle_llm=oracle_llm,
        verbose=static_args.sim.verbose,
        test_run=static_args.sim.test_run,
        amounts_per_run=amounts, # this contains the amounts of currencies that are being split each run, created in main
        currencies=currencies, # this contains the currencies to be split for each run
        agents_dict=agents, # this contains the agents for each run
        interactions_dict=args.interactions, # this contains the interactions for each run
        edge_case_instructions=args.env.edge_cases.selected_contract if args.env.edge_cases.selected_contract else "",
        include_reason=args.env.edge_cases.reason.include_reason,
        propose_decide_alignment=args.env.propose_decide_alignment,
        has_manners = (args.env.single_fixed_manners == "neutral"),
        ask_question=args.env.edge_cases.conditions.ask_question,
        ask_question_train=args.env.ask_question_train,
        set_fixed_agents=args.env.set_fixed_agents,
    )

# create llms to be used in context
def get_llms(args):
    args.model.azure_api.api_key = os.getenv("OPENAI_API_KEY") # set api key, ANA
    assistant_llm = GPT4Agent(llm = AsyncAzureChatLLM(**args.model.azure_api), **args.model.completion_config)
    user_llm = GPT4Agent(llm = AsyncAzureChatLLM(**args.model.azure_api), **args.model.completion_config)
    meta_llm = GPT4Agent(llm = AsyncAzureChatLLM(**args.model.azure_api), **args.model.completion_config)
    oracle_llm = GPT4Agent(llm = AsyncAzureChatLLM(**args.model.azure_api), **args.model.completion_config)
    return assistant_llm, user_llm, meta_llm, oracle_llm

def run(args):
    static_args = args
    #create a copy of the config file and experiment description for reference
    config_directory=f'{hydra.utils.get_original_cwd()}/experiments/{args.sim.sim_dir}/config_history'
    os.makedirs(config_directory, exist_ok=True)
    with open(f'{config_directory}/config_original', "w") as f: f.write(OmegaConf.to_yaml(args))  
    with open(f"{config_directory}/../description", "w") as f: f.write(args.sim.description)
    
    assistant_llm, user_llm, meta_llm, oracle_llm = get_llms(args)

    num_experiments = args.env.random.n_rand_iter
    original_currencies = args.env.currencies

    DATA_DIRS = []
    variable_args = []

    generate_agents(args)
    generate_interactions(args)
    
    sim_ids = []
    all_currencies = []
    amounts_per_run =  []
    cur_amount_min, cur_amount_max = float('inf'), float('-inf')
    # This loops generates num_experiments different data dictionaries for each run
    for i in range(num_experiments):
        # Make each data directory to save to for each separate experiment

        args.env.currencies = original_currencies
        # set run id, amounts, currency, and write into the current config
        generate_starting_message(args)
        generate_random_params(args)
        generate_agents(args)

        # Keep track of currencies to use during generalization

        all_currencies.append(args.env.currencies)

        amounts_per_run.append(args.env.amounts_per_run)

        # keep track of amounts to use during generalization
        for amount in args.env.amounts_per_run:
            if amount < cur_amount_min:
                cur_amount_min = amount
            if amount > cur_amount_max:
                cur_amount_max = amount

        args.sim.sim_id = f"generalization_{i}_{args.env.currencycounter}" if args.env.edge_cases.activate else f"{i}_{args.env.currencies}"

        sim_ids.append(args.sim.sim_id)

        with open(f'{config_directory}/id_{args.sim.sim_id}_config', "w") as f: f.write(OmegaConf.to_yaml(args))    

        DATA_DIR = f'{hydra.utils.get_original_cwd()}/experiments/{args.sim.sim_dir}/{args.sim.sim_id}'
        os.makedirs(DATA_DIR, exist_ok=True)

        DATA_DIRS.append(DATA_DIR)

        variable_args.append(copy.deepcopy(args))

    get_num_interactions(args)
    game_number = int(f"{int(1 if args.env.n_fixed_inter else 0)}{int(1 if args.env.n_mixed_inter else 0)}{int(1 if args.env.n_flex_inter else 0)}", 2)
    meta_module = importlib.import_module(f"scai.dictator_games.meta_prompts.dictator_{game_number}_meta_prompts")

    META_PROMPTS = meta_module.META_PROMPTS
    ############
    # scores stores the scores in the form of the amounts proposed for one context run
    scores = [[] for _ in range(num_experiments)]
    # stores the scores in the form of the amounts proposed for one context run
    questions = []
    ############

    # This stores all the scores for plotting as well as just the raw scores from each run 
    total_scores, all_score_lsts = [], []

    all_questions = []

    currencies_and_questions = {}

    system_messages = [[""] for _ in range(num_experiments)]
    # run meta-prompt
    for run in tqdm(range(args.env.n_runs)):

        # initialize context that has info for all of the runs in the args dictionaries
        context = create_context(static_args, variable_args, assistant_llm, user_llm, meta_llm, oracle_llm, Context,     
                                DICTATOR_TASK_PROMPTS, DECIDER_TASK_PROMPTS, META_PROMPTS)
        for i in range(num_experiments):
            context.buffer[i].save_system_context(model_id='system', **{
                'response': system_messages[i][run],
            })

        # run context - this runs the simulation
        all_proposals, question = context.run(run)


        # save results as csv
        for j in range(num_experiments):
            scores[j].append(all_proposals[j])

            save_as_csv(system_data=context.buffer[j]._system_memory.messages,
                        chat_data=context.buffer[j]._chat_memory.messages,
                        data_directory=DATA_DIRS[j], 
                        sim_name=args.sim.sim_dir,
                        sim_id=sim_ids[j],
                        run=run)
            # save results json
            with open(f'{DATA_DIRS[j]}/id_{sim_ids[j]}_run_{run}.json', 'w') as f:
                json.dump(context.buffer[j]._full_memory.messages, f)
        
        # update system message after each run
            system_message = copy.deepcopy(context.buffer[j].load_memory_variables(memory_type='system')['system'][-1]['response']) # replace current system message with the new one (i.e. new constitution)
            system_messages[j].append(system_message)

        questions.append(question)

    # deal with this later
    if args.env.currencies[0] not in currencies_and_questions:
        currencies_and_questions[args.env.currencies[0]] = []
    currencies_and_questions[args.env.currencies[0]].extend(questions)

    final_messages = [system_message[-1] for system_message in system_messages]
    all_contracts = []
    for system_message in final_messages:
        index = system_message.find("Principle:")
        if index == -1: index = 0
        all_contracts.append(system_messages[index:])

    # plot average user gain across runs
    for j in range(num_experiments):
        fixed_plot, flex_plot, fixed_bar, flex_bar, score_lsts = plot_results(data_directory=f"{config_directory}/../{sim_ids[j]}/graphs", 
                                                                            sim_name=args.sim.sim_dir,
                                                                            sim_id=sim_ids[j],
                                                                            scores=scores[j], # all I have to do is craft scores, and functionality is the same
                                                                            n_runs=args.env.n_runs,
                                                                            currencies=all_currencies[j], # at this point, currencies is decided
                                                                            amounts_per_run=amounts_per_run[j] # at this point, amounts_per_run is decided
                                                                            )
        total_scores.append([fixed_plot, flex_plot, fixed_bar, flex_bar])
        all_score_lsts.append(score_lsts)
        # all_questions.append(sum(questions) / len(questions))

        # save results
        with open(f"{config_directory}/../{sim_ids[j]}/results", "w") as f:
            f.write(str(fixed_plot[0][-1]) + "\n" + str(flex_plot[0][-1]))

    # make plots that averages across all experiments
    if num_experiments > 1:
        directory=f'{hydra.utils.get_original_cwd()}/experiments/{args.sim.sim_dir}/final_graphs'
        os.makedirs(directory, exist_ok=True)
        plot_all_averages(total_scores=total_scores, all_score_lsts=all_score_lsts, questions=currencies_and_questions, edge_case=args.env.edge_cases.test_edge_cases, currencies=args.env.currencies, n_runs=args.env.n_runs, directory=directory, sim_dir=args.sim.sim_dir, sim_id="all")

        return all_currencies, all_contracts, cur_amount_min, cur_amount_max, all_questions

# run simulator
@hydra.main(config_path="config", config_name="config")
def main(args: DictConfig) -> None:

    # if you are testing edge cases and you're reusing old data, then retrieve that data and set it 
    if args.env.edge_cases.test_edge_cases and not args.env.edge_cases.generate_new_data:
        existing_data = get_existing_data(args)
        amounts = existing_data['amounts']
        all_currencies = existing_data['currencies']
        all_contracts = existing_data['contracts']
    # Otherwise, make everything from scratch again
    elif not args.env.edge_cases.test_edge_cases:
        # Run the simulation
        all_currencies, all_contracts, cur_amount_min, cur_amount_max, _ = run(args)
        return
    # # ------------ CODE FROM THIS POINT ON IS RELTAED TO GENERALIZATION_v2 ------------ #
    #If you're not testing edge cases, then return
    oo_dist_q = []
    in_dist_q = []
    for currency in enumerate(all_currencies):
        args.env.currencies = [currency]

        minmax_amounts = [min(amounts), max(amounts)]

        contract = random.choice(all_contracts)

        prompt_string = create_prompt_string([currency], minmax_amounts, contract, args.env.edge_cases.prior)

        original_n_rand_iter, original_sim_dir, original_n_runs = set_args_2(args, prompt_string)

        args.env.edge_cases.test_edge_cases = True

        _, _, _, _, out_dist_questions = run(args)
        if args.env.edge_cases.conditions.currency.currencies[0] == currency:
            in_dist_q.append(sum(out_dist_questions) / len(out_dist_questions))
        else:
            oo_dist_q.append(sum(out_dist_questions) / len(out_dist_questions))
        reset_args_2(args, original_n_rand_iter, original_sim_dir, original_n_runs)

    plot_questions(oo_dist_q, in_dist_q, f'{hydra.utils.get_original_cwd()}/experiments/{args.sim.sim_dir}/question_graphs')
            

    # # ------------ CODE FROM THIS POINT ON IS RELTAED TO GENERALIZATION_v1 ------------ #
    # # If you're not testing edge cases, then return
    # if not args.env.edge_cases.test_edge_cases:
    #     return
    # # Otherwise, set the amounts according to the data you just generated
    # if args.env.edge_cases.generate_new_data:
    #     amounts = [cur_amount_min, cur_amount_max]
    # # Pick a contract from the list of contract generated
    # contract = agent_pick_contract(all_contracts)
    # # Create the prompt string for the flexible agent
    # prompt_string = create_prompt_string(all_currencies, amounts, contract, args.env.edge_cases.prior)
    # # Set the arguments according to the specified yaml arguments
    # set_args(args, prompt_string)
    # # Run the model again, testing generalization
    # run(args)

                         
if __name__ == '__main__':
    main()