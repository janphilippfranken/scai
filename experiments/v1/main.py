import hydra
from hydra import utils
from omegaconf import DictConfig

import json
from tqdm import tqdm
import pandas as pd
import os

from datetime import datetime
import warnings

warnings.filterwarnings('ignore')

# import episode
from scai.modules.episode.episode import Episode

# prompts 
from scai.modules.task.prompts import TASK_PROMPTS
from scai.modules.assistant.prompts import ASSISTANT_PROMPTS 
from scai.modules.user.prompts import USER_PROMPTS 
from scai.modules.meta_prompt.prompts import META_PROMPTS 

# llm class
from custom_chat_models.crfm import crfmChatLLM

# main arguments
from arguments import args

# visuals 
from visuals import plot_user_ratings, get_ratings

# save csvs
from utils import save_as_csv

# create episode
def create_episode(args, assistant_llm, user_llm, meta_llm):
    # episode params 
    return Episode.create(
        id=args.sim.episode_id,
        name=args.sim.episode_name,
        n_assistant=args.sim.n_assistant,
        n_user=args.sim.n_user,
        system_k=args.sim.system_k,
        chat_k=args.sim.chat_k,
        user_k=args.sim.user_k,
        assistant_k=args.sim.assistant_k,
        assistant_system_k=args.sim.assistant_system_k, 
        task_prompt=TASK_PROMPTS['task_prompt_1'], # TODO: make all of these part of config
        user_prompts=[USER_PROMPTS['user_prompt_1'], USER_PROMPTS['user_prompt_2']],
        assistant_prompts=[ASSISTANT_PROMPTS['assistant_prompt_1'], ASSISTANT_PROMPTS['assistant_prompt_1']],
        meta_prompt=META_PROMPTS['meta_prompt_1'],
        user_llm=user_llm,
        assistant_llm=assistant_llm,
        meta_llm=meta_llm,
        verbose=args.sim.verbose
    )

@hydra.main(config_path="config", config_name="config")
def main(args: DictConfig) -> None:
    
    # sim_res directory
    DATA_DIR = f'{hydra.utils.get_original_cwd()}/sim_res/{args.sim.episode_id}'

    # models
    assistant_llm = crfmChatLLM(**args.api.assistant)
    user_llm = crfmChatLLM(**args.api.user)
    meta_llm = crfmChatLLM(**args.api.meta)

    # create episode
    episode = create_episode(args, assistant_llm, user_llm, meta_llm)

    # save initial system message
    episode.buffer.save_context(system={'content': args.sim.system_message}, system_message_id='system_message_0')

    # run episode
    for _ in tqdm(range(args.sim.n_runs)):
        episode.run()
        save_as_csv(episode, DATA_DIR, args.sim.episode_id, args.sim.model)

    # plot user ratings
    df = get_ratings(pd.read_csv(f'{DATA_DIR}/{args.sim.episode_id}_{args.sim.model}.csv'))
    plot_user_ratings(df, plot_dir=DATA_DIR, episode_id=args.sim.episode_id, model=args.sim.model)

    # python main.py ++sim.verbose=false

if __name__ == '__main__':
    main()