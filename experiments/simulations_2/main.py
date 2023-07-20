import hydra
from omegaconf import DictConfig

from tqdm import tqdm
import pandas as pd
import json

# llm class
from scai.chat_models.crfm import crfmChatLLM
from langchain.chat_models import ChatOpenAI
from langchain.chat_models.base import BaseChatModel

# import context
from scai.games.game_2.context import Context

import copy

# prompts 
from scai.games.game_2.prompts.task.prompts import TASK_PROMPTS
from scai.games.game_2.prompts.assistant.prompts import ASSISTANT_PROMPTS 
from scai.games.game_2.prompts.user.prompts import USER_PROMPTS 
from scai.games.game_2.prompts.meta.prompts import META_PROMPTS
from scai.games.game_2.prompts.metrics.prompts import METRIC_PROMPTS     #No more metrics

# save and plot results
from utils import save_as_csv, plot_results, plot_average_results      # Change util functions
from plots import plot_cosine_similarity                                # Change plot functions

# create context
def create_context(
    args: DictConfig, 
    assistant_llm, 
    user_llm, 
    meta_llm,
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
        max_tokens_user=args.sim.max_tokens_user,
        max_tokens_assistant=args.sim.max_tokens_assistant,
        max_tokens_meta=args.sim.max_tokens_meta,
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

# run simulator
@hydra.main(config_path="config", config_name="config")
def main(args: DictConfig) -> None:
    
    # sim_res directory
    DATA_DIR = f'{hydra.utils.get_original_cwd()}/sim_res/{args.sim.sim_dir}/{args.sim.sim_id}'
    
    # llms
    is_crfm = 'openai' in args.sim.model_name # custom stanford models
    assistant_llm, user_llm, meta_llm = get_llms(args, is_crfm)
    
    # start system messages for assistant (key variables we are learning)
    system_message = args.sim.system_message
    meta_prompt = META_PROMPTS[args.sim.meta_prompt]
    meta_prompt_metrics = {meta_prompt.metrics[0]: " ", meta_prompt.metrics[1]: " "} # currently developer constitution and social constract
    
    # run meta-prompt
    for run in tqdm(range(args.sim.n_runs)):
        # initialise context
        context = create_context(args, assistant_llm, user_llm, meta_llm)
        context.buffer.save_system_context(model_id='system', **{
            'response': system_message, 
        })
        
        # run context
        context.run(args.sim.n_turns, run)
        
        # save results as csv
        save_as_csv(system_data=context.buffer._system_memory.messages,
                    chat_data=context.buffer._chat_memory.messages,
                    data_directory=DATA_DIR, 
                    sim_name=args.sim.sim_dir,
                    sim_id=args.sim.sim_id,
                    run=run,
                    collective_metric=METRIC_PROMPTS[args.sim.metric_prompt].collective_metric)
        # save results json
        with open(f'{DATA_DIR}/{args.sim.sim_dir}_id_{args.sim.sim_id}_run_{run}.json', 'w') as f:
            json.dump(context.buffer._full_memory.messages, f)
        
        # update system message after each run
        system_message = copy.deepcopy(context.buffer.load_memory_variables(memory_type='system')['system'][-1]['response']) # replace current system message with the new one (i.e. new constitution)
        meta_prompt_metrics = copy.deepcopy(context.buffer.load_memory_variables(memory_type='system')['system'][-1]['full_response']) # replace current system message with the new one (i.e. new constitution)
        
        # plot user ratings for the current run
        df = pd.read_csv(f'{DATA_DIR}/{args.sim.sim_dir}_id_{args.sim.sim_id}_run_{run}_user.csv')
        plot_results(df, DATA_DIR, args.sim.sim_dir, args.sim.sim_id, run, subjective_metric=METRIC_PROMPTS[args.sim.metric_prompt].subjective_metric, collective_metric=f'{METRIC_PROMPTS[args.sim.metric_prompt].collective_metric}_average')
    
    # plot average user ratings across runs
    plot_average_results(data_directory=DATA_DIR, 
                         sim_name=args.sim.sim_dir, 
                         sim_id=args.sim.sim_id, 
                         n_runs=args.sim.n_runs, 
                         subjective_metric=METRIC_PROMPTS[args.sim.metric_prompt].subjective_metric, 
                         collective_metric=f'{METRIC_PROMPTS[args.sim.metric_prompt].collective_metric}_average')      
    
    # plot cosine similarity between system messages (developer constituiton and social contracts and save csvs)
    plot_cosine_similarity(data_directory=DATA_DIR,
                           sim_name=args.sim.sim_dir,
                           sim_id=args.sim.sim_id,
                           n_runs=args.sim.n_runs,
                           metrics=META_PROMPTS[args.sim.meta_prompt].metrics)

if __name__ == '__main__':
    main()