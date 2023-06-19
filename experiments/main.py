import json
from tqdm import tqdm
import pandas as pd
from fire import Fire

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

DATA_DIR = 'sim_res' 

def save_as_csv(episode, episode_id, model):
    message_records = []
    for message_type, messages in episode.buffer.full_memory.message_dict.items():
        for msg in messages:
            message_records.append({
                'message_type': message_type, 
                'content': msg['message'].content, 
                'rating': msg['rating']
            })

    # convert to dataframe and save as csv
    pd.DataFrame(message_records).to_csv(f'{DATA_DIR}/{episode_id}_{model}.csv', index=False)

def create_episode(episode_id, assistant_llm, user_llm, meta_llm, verbose):
    # episode params  TODO: add all episode params to main arguments except id and name or allow for flex input here with argparse
    episode_params = {
        'id': episode_id,
        'name': episode_id,
        'n_assistant': args.sim.n_assistant,
        'n_user': args.sim.n_user,
        'system_k': args.sim.system_k,
        'chat_k': args.sim.chat_k,
        'user_k': args.sim.user_k,
        'assistant_k': args.sim.assistant_k,
        'assistant_system_k': args.sim.assistant_system_k,
    }

    # write parameters to a json file
    with open(f'{DATA_DIR}/{episode_id}.json', 'w') as json_file:
        json.dump(episode_params, json_file)

    return Episode.create(
        **episode_params,
        # prompts
        task_prompt=TASK_PROMPTS['task_prompt_1'],
        user_prompts=[USER_PROMPTS['user_prompt_1'], USER_PROMPTS['user_prompt_2']],
        assistant_prompts=[ASSISTANT_PROMPTS['assistant_prompt_1'], ASSISTANT_PROMPTS['assistant_prompt_1']],
        meta_prompt=META_PROMPTS['meta_prompt_1'],
        # llms
        user_llm=user_llm,
        assistant_llm=assistant_llm,
        meta_llm=meta_llm,
        # for debugging
        verbose=verbose,
    )

def main(episode_id='episode_0', verbose=False, system_message='You are a helpful AI assistant.', n_runs=3, model='gpt4'):

    # models
    # TODO: feed model args from command line to args.api
    assistant_llm = crfmChatLLM(**vars(args.api.assistant))
    user_llm = crfmChatLLM(**vars(args.api.user))
    meta_llm = crfmChatLLM(**vars(args.api.meta))

    episode = create_episode(episode_id, assistant_llm, user_llm, meta_llm, verbose)

    episode.buffer.save_context(system={'content': system_message}, system_message_id='system_message_0')

    for _ in tqdm(range(n_runs)):
        episode.run()
        save_as_csv(episode, episode_id, model)

    # create visuals
    df = get_ratings(pd.read_csv(f'{DATA_DIR}/{episode_id}_{model}.csv'))
    plot_user_ratings(df, plot_dir=DATA_DIR, episode_id=episode_id, model=model)

if __name__ == '__main__':
    Fire(main)