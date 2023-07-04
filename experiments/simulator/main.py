import hydra
from hydra import utils
from omegaconf import DictConfig

from tqdm import tqdm
import pandas as pd
import json

# llm class
from scai.chat_models.crfm import crfmChatLLM
from langchain.chat_models import ChatOpenAI

# import context
from scai.context.context import Context

# prompts 
from scai.prompts.task.prompts import TASK_PROMPTS
from scai.prompts.assistant.prompts import ASSISTANT_PROMPTS 
from scai.prompts.user.prompts import USER_PROMPTS 
from scai.prompts.meta_prompt.prompts import META_PROMPTS 
from scai.prompts.metrics.prompts import METRIC_PROMPTS

# main arguments
from arguments import args

# save as csv
from utils import save_as_csv, plot_results

# create context
def create_context(args, assistant_llm, user_llm, meta_llm):
    # context params
    return Context.create(
        id=args.sim.sim_id,
        name=args.sim.sim_dir,
        system_k=args.sim.system_k,
        chat_k=args.sim.chat_k,
        task_prompt=TASK_PROMPTS[args.sim.task_prompt],
        user_prompts=[USER_PROMPTS[user_prompt] for user_prompt in args.sim.user_prompts],
        assistant_prompts=[ASSISTANT_PROMPTS[assistant_prompt] for assistant_prompt in args.sim.assistant_prompts],
        meta_prompt=META_PROMPTS[args.sim.meta_prompt],
        metric_prompt=METRIC_PROMPTS[args.sim.metric_prompt],
        user_llm=user_llm,
        assistant_llm=assistant_llm,
        meta_llm=meta_llm,
        verbose=args.sim.verbose,
        test_run=args.sim.test_run,
        max_tokens_user=args.sim.max_tokens_user,
        max_tokens_assistant=args.sim.max_tokens_assistant,
        max_tokens_meta=args.sim.max_tokens_meta,
    )

@hydra.main(config_path="config", config_name="config")
def main(args: DictConfig) -> None:
    
    # sim_res directory
    DATA_DIR = f'{hydra.utils.get_original_cwd()}/sim_res/{args.sim.sim_dir}/{args.sim.sim_id}'

    # models
    is_crfm = 'openai' in args.sim.model_name # custom stanford models

    # llm
    if is_crfm:
        assistant_llm = crfmChatLLM(**args.api_crfm.assistant)
        user_llm = crfmChatLLM(**args.api_crfm.user)
        meta_llm = crfmChatLLM(**args.api_crfm.meta)
    else:
        assistant_llm = ChatOpenAI(**args.api_openai.assistant)
        user_llm = ChatOpenAI(**args.api_openai.user)
        meta_llm = ChatOpenAI(**args.api_openai.meta)

    # create context
    context = create_context(args, assistant_llm, user_llm, meta_llm)

    # save initial system message
    context.buffer.save_system_context(message_id='system', **{'response': args.sim.system_message})

    # run context
    for _ in tqdm(range(args.sim.n_runs)):
        context.run()
        # save context buffer messages as csv
        save_as_csv(data=context.buffer._memory.messages, 
                    data_directory=DATA_DIR, 
                    sim_name=args.sim.sim_dir,
                    sim_id=args.sim.sim_id)

    # save full context buffer messages as json
    with open(f'{DATA_DIR}/{args.sim.sim_dir}_{args.sim.sim_id}.json', 'w') as f:
        json.dump(context.buffer._memory.messages, f)

    # plot user ratings 
    df = pd.read_csv(f'{DATA_DIR}/{args.sim.sim_dir}_{args.sim.sim_id}_user.csv')
    plot_results(df, DATA_DIR, args.sim.sim_dir, args.sim.sim_id)
    
    # python main.py ++sim.verbose=false

if __name__ == '__main__':
    main()