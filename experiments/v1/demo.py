# written by patrick
import hydra
from omegaconf import DictConfig

from tqdm import tqdm
import pandas as pd

import warnings

warnings.filterwarnings('ignore')

import streamlit as st

from PIL import Image


# import episode
from scai.modules.episode.episode import Episode

# import prompt models
from scai.modules.task.models import TaskPrompt
from scai.modules.user.models import UserPrompt

# import prompts
from scai.modules.assistant.prompts import ASSISTANT_PROMPTS 
from scai.modules.user.prompts import USER_PROMPTS 
from scai.modules.meta_prompt.prompts import META_PROMPTS
from scai.modules.task.prompts import TASK_PROMPTS

# llm classes
from custom_chat_models.crfm import crfmChatLLM # custom crfm models
from langchain.chat_models import ChatOpenAI # TODO: add openai models

# main arguments
from arguments import args

# visuals 
from visuals import plot_user_ratings, get_ratings

# save csvs
from utils import save_as_csv

# streamlit setup for task, user, and LLM
TASK_SELECT, USER_SELECT, LLM_SELECT = [], [], []

for task_prompt in TASK_PROMPTS.values():
    TASK_SELECT.append(task_prompt.content)

for user_prompt in USER_PROMPTS.values():
    USER_SELECT.append(user_prompt.persona)

for llm in ["openai/gpt-3.5-turbo-0301", "openai/gpt-4-0314"]:
    LLM_SELECT.append(llm)

# heading 
st.write("You are collaborating with others to write a Wikipedia article.")

# task
st.subheader("Step 1: Task")

TASK = st.selectbox(    
    'Select a topic:',
    TASK_SELECT,
)

TASK_PROMPT = TaskPrompt(
        id="",
        task_type="",
        name="",
        role="system",
        content=TASK,
)

st.write("SELECTED TASK:", TASK_PROMPT.content)

# user personas
st.subheader("Step 2: Users")

PERSONAS = st.multiselect(
    'Select personas:',
    USER_SELECT,
)

SELECTED_USER_PROMPTS = []

for i, persona in enumerate(PERSONAS):
    user_prompt = UserPrompt(
        id=f'user_prompt_{i}',
        name="wikipedia_editor",
        max_tokens=50,
        persona=persona,
        role="system",
        content="""{persona} {task}""",
    )
    SELECTED_USER_PROMPTS.append(user_prompt)

st.write("SELECTED PERSONAS:", PERSONAS)

# record how many users were selected (hacky to get assistatn messages for now)
N_USER = len(PERSONAS)

# llm
st.subheader("Step 3: LLM")

# model
LLM = st.selectbox(    
    'Select LLM (currently only supports crfm openai API):',
    LLM_SELECT,
)

# api key
API_KEY = st.text_input(    
    'Enter Key:',
)

# api key
VERBOSE = st.selectbox(    
    'Verbose (if false, this willl use tokens!):',
    [True, False],
)

# create episode
def create_episode(args, assistant_llm, user_llm, meta_llm, task_prompt, user_prompts):
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
        task_prompt=task_prompt,
        user_prompts=user_prompts,
        assistant_prompts=[ASSISTANT_PROMPTS['assistant_prompt_1']] * N_USER, # need to update this
        meta_prompt=META_PROMPTS['meta_prompt_1'],
        user_llm=user_llm,
        assistant_llm=assistant_llm,
        meta_llm=meta_llm,
        verbose=args.sim.verbose
    )

@hydra.main(config_path="config", config_name="demo")
def run(args: DictConfig) -> None:

    # args.sim.n_user = N_USER
    # args.sim.n_assistant = N_USER # for now these are the

    # # sim_res directory
    DATA_DIR = f'{hydra.utils.get_original_cwd()}/sim_res/{args.sim.episode_id}'

    # # models. TODO: add openai api
    # args.sim.verbose = VERBOSE
    # args.api.assistant.crfm_api_key = API_KEY
    # args.api.user.crfm_api_key = API_KEY
    # args.api.meta.crfm_api_key = API_KEY
    # args.api.assistant.model_name = LLM
    # args.api.user.model_name = LLM
    # args.api.meta.model_name = LLM
    # args.sim.n_user = N_USER
    # args.sim.n_assistant = N_USER

    # assistant_llm = crfmChatLLM(**args.api.assistant)
    # user_llm = crfmChatLLM(**args.api.user)
    # meta_llm = crfmChatLLM(**args.api.meta)

    # # create episode
    # episode = create_episode(args, assistant_llm, user_llm, meta_llm, task_prompt, SELECTED_USER_PROMPTS)

    # # save initial system message
    # episode.buffer.save_context(system={'content': args.sim.system_message}, system_message_id='system_message_0')

    # # run episode
    # for _ in tqdm(range(args.sim.n_runs)):
    #     episode.run()
    #     save_as_csv(episode, DATA_DIR, args.sim.episode_id, args.sim.model)

    # # plot user ratings
    # df = pd.read_csv(f'{DATA_DIR}/{args.sim.episode_id}_{args.sim.model}.csv')
    # plot_df = get_ratings(df)
    # plot_user_ratings(plot_df, plot_dir=DATA_DIR, episode_id=args.sim.episode_id, model=args.sim.model, pdf=False)

    # plot user satisfaction
    st.write("Subjective Helpfulness Ratings for the AI Assistant Responses for each User")

    image = Image.open(f'{DATA_DIR}/{args.sim.episode_id}_demo.jpg')
    # image = Image.open(f'{DATA_DIR}/{args.sim.episode_id}_gpt-4-0313.jpg') #  hack for plot
    

    
    # 'sim_res/episode_1/episode_1_gpt-4-031.jpg4'

    st.image(image)

    # show system messages of assistant 
    st.write("System Messages used By the AI Assistant (revised after each epoch using meta-prompt, starting with an empty message)")
    # print working direcotry
   
    df = pd.read_csv(f'{DATA_DIR}/{args.sim.episode_id}_demo.csv')

    df_system = df[df['message_type'] == 'system']['response']
    df_system = df_system.reset_index()

    SYSTEM_MESSAGES = []
    # Iterate over the 'Assistant System Message' column
    for system_messsage in list(df_system['response']):
        SYSTEM_MESSAGES.append(system_messsage)

    st.write("SYSTEM MESSAGES:", SYSTEM_MESSAGES)

    df_user = df[(df['message_type'] == 'user') & (df['conversation_id'] == 1)]['response']
    df_user = df_user.reset_index()

    USER_MESSAGES = []
    # Iterate over the 'Assistant System Message' column
    for user_messsage in list(df_user['response']):
        USER_MESSAGES.append(user_messsage)

    st.write("USER 1 (Internet Troll) FEEDBACK:", USER_MESSAGES)

    df_assistant = df[(df['message_type'] == 'assistant') & (df['conversation_id'] == 1)]['response']
    df_assistant = df_assistant.reset_index()


    ASSISTANT_MESSAGES = []
    # Iterate over the 'Assistant System Message' column
    for assistant_messsage in list(df_assistant['response']):
        ASSISTANT_MESSAGES.append(assistant_messsage)

    st.write("ASSISTANT RESPONSE TO USER 1:", ASSISTANT_MESSAGES)


    df_user = df[(df['message_type'] == 'user') & (df['conversation_id'] == 2)]['response']
    df_user = df_user.reset_index()

    USER_MESSAGES = []
    # Iterate over the 'Assistant System Message' column
    for user_messsage in list(df_user['response']):
        USER_MESSAGES.append(user_messsage)

    st.write("USER 2 (Wikipedia editor) FEEDBACK:", USER_MESSAGES)

    df_assistant = df[(df['message_type'] == 'assistant') & (df['conversation_id'] == 2)]['response']
    df_assistant = df_assistant.reset_index()


    ASSISTANT_MESSAGES = []
    # Iterate over the 'Assistant System Message' column
    for assistant_messsage in list(df_assistant['response']):
        ASSISTANT_MESSAGES.append(assistant_messsage)

    st.write("ASSISTANT RESPONSE TO USER 2:", ASSISTANT_MESSAGES)


    

if st.button('run'): run()