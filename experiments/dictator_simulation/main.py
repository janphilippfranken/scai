import hydra
from omegaconf import DictConfig

from tqdm import tqdm
import json

# llm class
from scai.chat_models.crfm import crfmChatLLM
from langchain.chat_models import ChatOpenAI
from langchain.chat_models.base import BaseChatModel


import copy
import importlib

# save and plot results
from utils import save_as_csv
from plots import plot_results

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
        task_prompt_dictator = DICTATOR_TASK_PROMPTS[args.environment.task_prompt],
        task_prompt_decider = DECIDER_TASK_PROMPTS[args.environment.task_prompt],
        meta_prompt=META_PROMPTS[args.environment.meta_prompt],
        user_llm=user_llm,
        assistant_llm=assistant_llm,
        meta_llm=meta_llm,
        verbose=args.sim.verbose,
        test_run=args.sim.test_run,
        amounts_per_run=args.environment.amounts_per_run,
        n_fixed_inter=args.environment.n_fixed_inter,
        n_mixed_inter=args.environment.n_mixed_inter,
        n_flex_inter=args.environment.n_flex_inter,
        currencies=args.environment.currencies,
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
def get_interactions(
    args: DictConfig,
    run: int,
) -> None:
    
    run_list = args.interactions.runs[f"run_{run+1}"]

    args.environment.n_fixed_inter = sum(1 for s in run_list if s.count("flex") == 0)
    args.environment.n_mixed_inter = sum(1 for s in run_list if s.count("flex") == 1)
    args.environment.n_flex_inter = sum(1 for s in run_list if s.count("flex") == 2)


# run simulator
@hydra.main(config_path="config", config_name="config")
def main(args: DictConfig) -> None:
    # sim_res directory
    DATA_DIR = f'{hydra.utils.get_original_cwd()}/experiments/{args.sim.sim_dir}/{args.sim.sim_id}'
    
    # llms
    is_crfm = 'openai' in args.sim.model_name # custom stanford models
    assistant_llm, user_llm, meta_llm = get_llms(args, is_crfm)
    
    system_message = args.sim.system_message
    system_messages = []
    scores = []
    # run meta-prompt
    for run in tqdm(range(args.environment.n_runs)):
        # initialise context

        if args.interactions.all_same: 
            get_interactions(args, 0)
        else:
            get_interactions(args, run)

        n_fixed = 1 if args.environment.n_fixed_inter else 0
        n_mixed = 1 if args.environment.n_mixed_inter else 0
        n_flex = 1 if args.environment.n_flex_inter else 0

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
    plot_results(data_directory=DATA_DIR, 
                         sim_name=args.sim.sim_dir,
                         sim_id=args.sim.sim_id,
                         scores=scores,
                         n_runs=args.environment.n_runs,
                         currencies=args.environment.currencies,
                         interactions=args.interactions,
                         amounts_per_run=args.environment.amounts_per_run)
                         
if __name__ == '__main__':
    main()