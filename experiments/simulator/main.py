import hydra
from hydra import utils
from omegaconf import DictConfig

from tqdm import tqdm
import pandas as pd

# import context
from scai.modules.context.context import Context

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


from utils import save_as_csv

# create context
def create_context(args, assistant_llm, user_llm, meta_llm):
    # context params
    return Context.create(
        id=args.sim.context_id,
        name=args.sim.context_name,
        n_assistant=args.sim.n_assistant,
        n_user=args.sim.n_user,
        system_k=args.sim.system_k,
        chat_k=args.sim.chat_k,
        user_k=args.sim.user_k,
        assistant_k=args.sim.assistant_k,
        assistant_system_k=args.sim.assistant_system_k, 
        task_prompt=TASK_PROMPTS[args.sim.task_prompt],
        user_prompts=[USER_PROMPTS[user_prompt] for user_prompt in args.sim.user_prompts],
        assistant_prompts=[ASSISTANT_PROMPTS[assistant_prompt] for assistant_prompt in args.sim.assistant_prompts],
        meta_prompt=META_PROMPTS[args.sim.meta_prompt],
        user_llm=user_llm,
        assistant_llm=assistant_llm,
        meta_llm=meta_llm,
        verbose=args.sim.verbose
    )

@hydra.main(config_path="config", config_name="config")
def main(args: DictConfig) -> None:
    
    # sim_res directory
    DATA_DIR = f'{hydra.utils.get_original_cwd()}/sim_res/{args.sim.context_id}'

    # models
    assistant_llm = crfmChatLLM(**args.api.assistant)
    user_llm = crfmChatLLM(**args.api.user)
    meta_llm = crfmChatLLM(**args.api.meta)

    # create context
    context = create_context(args, assistant_llm, user_llm, meta_llm)

    # save initial system message
    context.buffer.save_context(system={'content': args.sim.system_message}, system_message_id='system_message_0')

    # run context
    for _ in tqdm(range(args.sim.n_runs)):
        context.run()
        save_as_csv(context, DATA_DIR, args.sim.context_id, args.sim.model)

    # # plot user ratings
    df = get_ratings(pd.read_csv(f'{DATA_DIR}/{args.sim.context_id}_{args.sim.model}.csv'))
    plot_user_ratings(df, plot_dir=DATA_DIR, context_id=args.sim.context_id, model=args.sim.model, pdf=True)

    # python main.py ++sim.verbose=false

if __name__ == '__main__':
    main()