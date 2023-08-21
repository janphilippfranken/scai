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
from scai.games.buyer_seller.game import Game

import copy

# prompts 
from scai.games.buyer_seller.prompts.task.prompts import TASK_PROMPTS
from scai.games.buyer_seller.prompts.buyer.prompts import BUYER_PROMPTS
from scai.games.buyer_seller.prompts.seller.prompts import SELLER_PROMPTS
from scai.games.buyer_seller.prompts.meta.prompts import META_PROMPTS

# save and plot results
from utils import save_as_csv, concatenate_csv

# create game
def create_game(
    args: DictConfig, 
    buyer_llm,
    seller_llm,
    meta_llm,
) -> "Game":
    """
    Create a game.
    """
    return Game.create(
        _id=args.sim.sim_id,
        name=args.sim.sim_dir,
        buyer_llm=buyer_llm,
        seller_llm=seller_llm,
        meta_llm=meta_llm,
        task_prompt=TASK_PROMPTS[args.sim.task_prompt],
        buyer_prompt=BUYER_PROMPTS[args.sim.buyer_prompt],
        seller_prompt=SELLER_PROMPTS[args.sim.seller_prompt],
        meta_prompt=META_PROMPTS[args.sim.meta_prompt],
        verbose=args.sim.verbose,
        max_tokens_meta=args.sim.max_tokens_meta,
    )

def get_llms(
    args: DictConfig,         
    is_crfm: bool,
) -> BaseChatModel:
    if is_crfm:
        buyer_llm = crfmChatLLM(**args.api_crfm.buyer)
        seller_llm = crfmChatLLM(**args.api_crfm.seller)
        meta_llm = crfmChatLLM(**args.api_crfm.meta)
    else:
        buyer_llm = ChatOpenAI(**args.api_openai.buyer)
        seller_llm = ChatOpenAI(**args.api_openai.seller)
        meta_llm = ChatOpenAI(**args.api_openai.meta)
    return buyer_llm, seller_llm, meta_llm

# run simulator
@hydra.main(config_path="config", config_name="config")
def main(args: DictConfig) -> None:
    
    # sim_res directory
    DATA_DIR = f'{hydra.utils.get_original_cwd()}/sim_res/{args.sim.sim_dir}/{args.sim.sim_id}'
    
    # llms
    is_crfm = 'openai' in args.sim.model_name # custom stanford models
    buyer_llm, seller_llm, meta_llm = get_llms(args, is_crfm)
    
    # start system messages for buyer
    system_message_buyer = args.sim.system_message_buyer
    system_message_seller = args.sim.system_message_seller
    meta_prompt = META_PROMPTS[args.sim.meta_prompt]
    
    # run meta-prompt
    for run in tqdm(range(args.sim.n_runs)):
        # initialise game
        game = create_game(args, buyer_llm, seller_llm, meta_llm)
        game.buffer.save_system_context(model_id='system', **{
                'response': {
                'system_message_buyer': system_message_buyer,
                'system_message_seller': system_message_seller,
            }
        })
        
        # run context
        game.run(run)
        
        # save results as csv
        save_as_csv(system_data=game.buffer._system_memory.messages,
                    chat_data=game.buffer._chat_memory.messages,
                    data_directory=DATA_DIR, 
                    sim_name=args.sim.sim_dir,
                    sim_id=args.sim.sim_id,
                    run=run)
        # save results json
        with open(f'{DATA_DIR}/{args.sim.sim_dir}_id_{args.sim.sim_id}_run_{run}.json', 'w') as f:
            json.dump(game.buffer._full_memory.messages, f)
        
        # update system message after each run
        system_message_buyer = copy.deepcopy(game.buffer.load_memory_variables(memory_type='system')['system'][-1]['response']['system_message_buyer']) 
        system_message_seller = copy.deepcopy(game.buffer.load_memory_variables(memory_type='system')['system'][-1]['response']['system_message_seller'])
    
    # create average csv
    concatenate_csv(data_directory=DATA_DIR,
                    sim_name=args.sim.sim_dir,
                    sim_id=args.sim.sim_id,
                    n_runs=args.sim.n_runs)
        
if __name__ == '__main__':
    main()