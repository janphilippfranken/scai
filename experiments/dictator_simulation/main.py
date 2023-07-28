import hydra
from omegaconf import DictConfig

from tqdm import tqdm
import pandas as pd
import json

# llm class
from scai.chat_models.crfm import crfmChatLLM
from langchain.chat_models import ChatOpenAI
from langchain.chat_models.base import BaseChatModel

from scai.games.dictator_games.all_prompts.user_class import UserPrompt
from scai.games.dictator_games.all_prompts.user_prompts import utilities_dict_for_all, content


import copy
import importlib

# save and plot results
from utils import save_as_csv
from plots import plot_average_results, plot_cosine_similarity   

# prompts 
def import_prompts(game_number: int) -> None:
    task_module = importlib.import_module(f"scai.games.dictator_games.dictator_{game_number}.prompts.task_prompts")
    assistant_module = importlib.import_module(f"scai.games.dictator_games.dictator_{game_number}.prompts.assistant_prompts")
    user_module = importlib.import_module(f"scai.games.dictator_games.dictator_{game_number}.prompts.user_prompts")
    meta_module = importlib.import_module(f"scai.games.dictator_games.dictator_{game_number}.prompts.meta_prompts")
    Context = importlib.import_module(f"scai.games.dictator_games.dictator_{game_number}.context")
    DICTATOR_TASK_PROMPTS, DECIDER_TASK_PROMPTS = task_module._DICTATOR_TASK_PROMPTS, task_module._DECIDER_TASK_PROMPTS
    ASSISTANT_PROMPTS, USER_PROMPTS = assistant_module.ASSISTANT_PROMPTS, user_module.USER_PROMPTS
    META_PROMPTS = meta_module.META_PROMPTS
    return DICTATOR_TASK_PROMPTS, DECIDER_TASK_PROMPTS, ASSISTANT_PROMPTS, USER_PROMPTS, META_PROMPTS, Context                     

# create context
def create_context(
    args: DictConfig, 
    assistant_llm, 
    user_llm, 
    meta_llm,
    Context,
    DICTATOR_TASK_PROMPTS, 
    DECIDER_TASK_PROMPTS, 
    ASSISTANT_PROMPTS, 
    USER_PROMPTS, 
    META_PROMPTS
) -> "Context":
    """
    Create context
    """
    return Context.create(
        _id=args.sim.sim_id,
        name=args.sim.sim_dir,
        task_prompt_dictator = DICTATOR_TASK_PROMPTS[args.sim.task_prompt],
        task_prompt_decider = DECIDER_TASK_PROMPTS[args.sim.task_prompt],
        user_prompts=[USER_PROMPTS[user_prompt] for user_prompt in args.sim.user_prompts],
        assistant_prompts=[ASSISTANT_PROMPTS[assistant_prompt] for assistant_prompt in args.sim.assistant_prompts],
        meta_prompt=META_PROMPTS[args.sim.meta_prompt],
        user_llm=user_llm,
        assistant_llm=assistant_llm,
        meta_llm=meta_llm,
        verbose=args.sim.verbose,
        test_run=args.sim.test_run,
        n_fixed_inter = args.sim.n_fixed_inter,
        n_mixed_inter = args.sim.n_mixed_inter,
        n_flex_inter = args.sim.n_flex_inter,
    )

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

def create_users(agents_dict, currencies, n_fixed, n_mixed, n_flex):
    fixed_prompts = []
    if n_fixed or n_mixed:
        for agent in agents_dict.fixed_agents:
            utilities = ""
            for currency in currencies:
                utilities += utilities_dict_for_all[agent.utilities.currency].format(currency)
            fixed_prompts.append(UserPrompt(
                id=agent.name,
                utility=utilities,
                utilies_dict=utilities_dict_for_all,
                manners=agent.manners,
                role="system",
                content=content
            ))
    flex_prompts = []
    if n_flex or n_mixed:
        for agent in agents_dict.flex_agents:
            flex_prompts.append(AssistantPrompt(
                id=agent.name,
                role="system",
                manners=agent.manners,
                content="""{task}"""
            ))

    return fixed_prompts, flex_prompts


# run simulator
@hydra.main(config_path="config", config_name="config")
def main(args: DictConfig) -> None:

    n_fixed = 1 if args.environment.n_fixed_inter else 0
    n_mixed = 1 if args.environment.n_mixed_inter else 0
    n_flex = 1 if args.environment.n_flex_inter else 0

    
    # determines the type of game based on the number of fixed, mixed, and flexible interactions
    game_number = int(f"{int(n_fixed)}{int(n_mixed)}{int(n_flex)}", 2)

    DICTATOR_TASK_PROMPTS, DECIDER_TASK_PROMPTS, ASSISTANT_PROMPTS, USER_PROMPTS, META_PROMPTS, Context = import_prompts(game_number)

    agents = create_users(args.agents, args.environment.currencies, n_fixed, n_mixed, n_flex)
    
    # get user social contract
    # task_connective = USER_PROMPTS['user_prompt_1'].utilities_dict
    # social_contract = f"You are {args.sim.utility} {task_connective[args.sim.utility].split(args.sim.utility)[1]}"

    # sim_res directory
    DATA_DIR = f'{hydra.utils.get_original_cwd()}/sim_res/{args.sim.sim_dir}/{args.sim.sim_id}'
    
    # llms
    is_crfm = 'openai' in args.sim.model_name # custom stanford models
    assistant_llm, user_llm, meta_llm = get_llms(args, is_crfm)
    
    system_message = args.sim.system_message
    system_messages = []
    scores = []
    # run meta-prompt
    for run in tqdm(range(args.sim.n_runs)):
        # initialise context
        context = create_context(args, assistant_llm, user_llm, meta_llm, Context,     
                                 DICTATOR_TASK_PROMPTS, DECIDER_TASK_PROMPTS, ASSISTANT_PROMPTS, USER_PROMPTS, META_PROMPTS)
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
    plot_average_results(data_directory=DATA_DIR, 
                         sim_name=args.sim.sim_dir, 
                         sim_id=args.sim.sim_id, 
                         scores=scores)      
    
    # plot cosine similarity between system messages (developer constituiton and social contracts and save csvs)
    # plot_cosine_similarity(data_directory=DATA_DIR,
    #                        sim_name=args.sim.sim_dir,
    #                        sim_id=args.sim.sim_id,
    #                        social_contract="Social Contract: " + social_contract,
    #                        system_messages=system_messages)

if __name__ == '__main__':
    main()