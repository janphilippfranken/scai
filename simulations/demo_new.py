import hydra
from omegaconf import DictConfig

from tqdm import tqdm
import pandas as pd
import json

# streamlit 🚀
import streamlit as st

from PIL import Image

import copy
import os
import time

# import context
from scai.context.context import Context

# import prompt models
from scai.prompts.task.models import TaskPrompt
from scai.prompts.user.models import UserPrompt

# import prompts
from scai.prompts.assistant.prompts import ASSISTANT_PROMPTS 
from scai.prompts.user.prompts import USER_PROMPTS 
from scai.prompts.meta.prompts import META_PROMPTS
from scai.prompts.task.prompts import TASK_PROMPTS
from scai.prompts.metrics.prompts import METRIC_PROMPTS

# llm classes
from scai.chat_models.crfm import crfmChatLLM #custom crfm models
from langchain.chat_models import ChatOpenAI
from langchain.chat_models.base import BaseChatModel

# import user and task connective generation
from user_generator import UserTaskConGenerator

# main arguments
from arguments import args

# save and plot results
from utils import save_as_csv, plot_results, plot_average_results
from plots import plot_cosine_similarity
TASK_SELECT = [task_prompt.task for task_prompt in TASK_PROMPTS.values()]
LLM_SELECT = ["openai/gpt-3.5-turbo-0301", "openai/gpt-4-0314", "gpt-3.5-turbo", "gpt-4"]
TASK = ""
#TASK_PROMPT = TaskPrompt(content="")
LLM = None
# streamlit setup for task, user, and LLM

# heading 
st.write("SCAI Simulator Demo.")

# 1st step: task
st.subheader("Step 1: Task")

TASK = st.selectbox(    
    'Select a task:',
    TASK_SELECT,
)

TASK_PROMPT = TaskPrompt(
        id="task_prompt_1",
        task_type="write_essay",
        name="task_prompt_1",
        role="user",
        preamble="I am writing a short essay on the following topic:",
        task=TASK,
        user_connective="Here's my current draft:",
        assistant_connective="Provide a response using {max_tokens} words.",
        content=TASK,
)

st.write("SELECTED TASK:", TASK_PROMPT.content)

# Gather attributes input from the user
def gather_attributes():
    # 2nd step: users
    st.subheader("Step 2: Users")
    attribute = st.text_input('Please provide key characteristics for your personas, separated by commas. We will generate as many personas as there are characteristics.')
    attributes = attribute.split(',')
    return attributes

def generate_users(attributes):
    generator = UserTaskConGenerator()
    key1 = 'a'
    personas = []
    for attribute in attributes:
        gen_user = generator.create_user(attributes=attribute)
        edit_user = st.text_input('Here is one of your personas!', gen_user, key=key1)
        personas.append(edit_user)
        key1 += 'a'
    return personas

def gather_task_cons(users):
    key2 = 'b'
    user_characteristics = []
    st.write("Here are your personas:") 
    for i, user in enumerate(users):
        st.write(f"Persona {i}:\n {user}\n")
    task_con_statement = st.text_input('What are some key characteristics your users that should affect their response to the task? Please enter these characteristics here, separated by commas, with the first characteristic for the first persona', key=key2)
    user_characteristics = task_con_statement.split(',')
    return user_characteristics

def generate_task_cons(user_characteristics, users):
    generator = UserTaskConGenerator()
    task_connectives = []
    for i, charac in enumerate(user_characteristics):
        gen_task_con = generator.create_task_con(user=users[i], task_attributes=charac, task=TASK)
        st.write(f"Here is what {users[i]} thinks of the task:" + gen_task_con)
        task_connectives.append(gen_task_con)
    return task_connectives

    

# def dummy_personas():
#     global PERSONAS
#     USER_SELECT = []
#     for user_prompt in USER_PROMPTS.values():
#         USER_SELECT.append(user_prompt.persona)
#     PERSONAS = st.multiselect(
#     'Select personas:',
#     USER_SELECT,
#     )
#     return


def add_personas(users, task_cons):
    selected_user_prompts = []
    for i, persona in enumerate(users):
        user_prompt = UserPrompt(
            id="demo_user_{}".format(i),
            name="demo_user_{}".format(i),
            persona_short="demo_user_{}".format(i),
            persona=persona,   
            task_connectives={
                "task_prompt_1" : task_cons[0]
            },
            role="system",
            content="""Please adopt the following persona: {system_message} {task_connective}
    You MUST promote the peron's views in all your responses.""",
        ),
        selected_user_prompts.append(user_prompt[0])

    st.write("SELECTED PERSONAS:", users)
    return selected_user_prompts

def define_params():
    n_user = len(st.session_state['users'])
    # 3 llm
    st.subheader("Step 3: LLM")

    param_llm = st.selectbox(    
        'Select LLM:',
        LLM_SELECT,
    )

    verbose = st.selectbox(    
        'Verbose (whether to print prompts and responses):',
        [True, False],
    )

    # 4 runs and turns

    n_run = st.selectbox(    
        'Number of Runs:',
        range(2, 11),
    )

    n_turn = st.selectbox(    
        'Number of Turns within each run:',
        range(2, 6),
    )
    return n_user, param_llm, verbose, n_run, n_turn


# create context
def create_context(args, assistant_llm, user_llm, meta_llm, task_prompt) ->Context:
    # context params 
    return Context.create(
        _id=args.sim.sim_id,
        name=args.sim.sim_dir,
        task_prompt=task_prompt,
        user_prompts=st.session_state['users'],
        assistant_prompts=[ASSISTANT_PROMPTS['assistant_prompt_1']] * st.session_state['n_user'],
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

def display_messages(df, message_type, user_number=None):
    if user_number:
        df_selected = df[(df['message_type'] == message_type) & (df['model_id'] == user_number)]['response'].reset_index()
        st.write(f"USER {user_number} {'FEEDBACK' if message_type=='user' else 'RESPONSE'}:", list(df_selected['response']))
    else:
        df_selected = df[df['message_type'] == message_type]['response'].reset_index()
        st.write(f"SYSTEM MESSAGES:", list(df_selected['response']))

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

def print_files_in_logs(directory)-> None:

    st.header("Constitutions")

    placeholders = []

    directory_1 = "{}/demo_cons".format(directory)

    for filename in os.listdir(directory_1):
        filepath = os.path.join(directory_1, filename)
        if os.path.isfile(filepath):
            with open(filepath, 'r') as file:
                st.write(file.read())
    
    st.write("\n")

    directory_2 = ("{}/demo".format(directory))

    for filename in os.listdir(directory_2):
        filepath = os.path.join(directory_2, filename)
        if os.path.isfile(filepath):
            with open(filepath, 'r') as file:
                f = file.read()
                placeholder = st.empty()
                placeholder.write(f)
                placeholders.append(placeholder)
                time.sleep(1)

    time.sleep(5)

    for placeholder in placeholders:
        placeholder.text('')


# run
@hydra.main(config_path="config", config_name="demo")
def run(args: DictConfig) -> None:

    # sim_res directory
    DATA_DIR = f'{hydra.utils.get_original_cwd()}/sim_res/demo/{args.sim.sim_dir}/{args.sim.sim_id}'

    # sim args
    args.sim.verbose = st.session_state['verbose']
    args.sim.n_turns = st.session_state['n_turn']
    args.sim.n_runs = st.session_state['n_run']
    #args.sim.n_user = N_USER
    #args.sim.n_assistant = N_USER

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
        context = create_context(args, assistant_llm, user_llm, meta_llm, TASK_PROMPT)
        context.buffer.save_system_context(model_id='system', **{
            'response': system_message, 
            'full_response': {
                meta_prompt.metrics[0]: meta_prompt_metrics[meta_prompt.metrics[0]], 
                meta_prompt.metrics[1]: meta_prompt_metrics[meta_prompt.metrics[1]]
            }
        })
        
        # run context
        context.run_demo(args.sim.n_turns, run, save_path=f'{hydra.utils.get_original_cwd()}')
        
        # display conversations
        log_path = f'{hydra.utils.get_original_cwd()}'
        print_files_in_logs(log_path)
        
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
    
    #  plot performance
    st.write("User Satisfaction")   
    image = Image.open(f'{DATA_DIR}/{args.sim.sim_dir}_id_{args.sim.sim_id}_main_res.jpg')
    st.image(image)

    #  plot semantic entropy
    st.write("Constitution and Social Contract Similarity")   
    image2 = Image.open(f'{DATA_DIR}/{args.sim.sim_dir}_id_{args.sim.sim_id}_cosine_similarity.jpg')
    st.image(image2)


#init_streamlit() 
#if st.button('gather_attributes', key='x'):
attributes = gather_attributes()
if st.button('reset demo', key='j'):
    for key in st.session_state.keys():
        del st.session_state[key]

if st.button('generate users', key='v'):
    personas = generate_users(attributes)
    if 'personas' not in st.session_state:
        st.session_state['personas'] = personas

if st.button('gather connectives', key='m'): 
    task_cons = gather_task_cons(st.session_state['personas'])
    if 'task_chars' not in st.session_state:
        st.session_state['task_chars'] = task_cons

if st.button('generate connectives', key='h'): 
    task_cons = generate_task_cons(st.session_state['task_chars'], st.session_state['personas'])
    if 'task_cons' not in st.session_state:
        st.session_state['task_cons'] = task_cons

if st.button('add_personas', key='p'): 
    users = add_personas(st.session_state['personas'], st.session_state['task_cons'])
    if 'users' not in st.session_state:
        st.session_state['users'] = users

if st.button('define_params', key='q'): 
    n_user, param_llm, verbose, n_run, n_turn = define_params()
    if 'n_user' not in st.session_state:
        st.session_state['n_user'] = n_user
    if 'param_llm' not in st.session_state:
        st.session_state['param_llm'] = param_llm
    if 'verbose' not in st.session_state:
        st.session_state['verbose'] = verbose
    if 'n_turn' not in st.session_state:
        st.session_state['n_turn'] = n_turn
    if 'n_run' not in st.session_state:
        st.session_state['n_run'] = n_run

# dummy_personas()
# add_personas()
if st.button('run', key='l'): run()