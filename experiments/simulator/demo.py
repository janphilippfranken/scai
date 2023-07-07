# import hydra
# from omegaconf import DictConfig

# from tqdm import tqdm
# import pandas as pd

# # streamlit 🚀
# import streamlit as st

# from PIL import Image


# # import context
# from scai.context.context import Context

# # import prompt models
# from scai.task.models import TaskPrompt
# from scai.agents.user.models import UserPrompt

# # import prompts
# from scai.agents.assistant.prompts import ASSISTANT_PROMPTS 
# from scai.agents.user.prompts import USER_PROMPTS 
# from scai.agents.meta.prompts import metaS
# from scai.task.prompts import TASK_PROMPTS

# # llm classes
# from custom_chat_models.crfm import crfmChatLLM # custom crfm models
# from langchain.chat_models import ChatOpenAI 

# # main arguments
# from arguments import args

# # visuals 
# from visuals import plot_user_ratings, get_ratings

# # save csvs
# from utils import save_as_csv

# # streamlit setup for task, user, and LLM
# TASK_SELECT, USER_SELECT, LLM_SELECT = [], [], []

# for task_prompt in TASK_PROMPTS.values():
#     TASK_SELECT.append(task_prompt.content)

# for user_prompt in USER_PROMPTS.values():
#     USER_SELECT.append(user_prompt.persona)

# for llm in ["openai/gpt-3.5-turbo-0301", "openai/gpt-4-0314", "gpt-3.5-turbo", "gpt-4"]:
#     LLM_SELECT.append(llm)

# # heading 
# st.write("SCAI Simulator Demo.")

# # 1 task
# st.subheader("Step 1: Task")

# TASK = st.selectbox(    
#     'Select a task:',
#     TASK_SELECT,
# )

# TASK_PROMPT = TaskPrompt(
#         id="",
#         task_type="",
#         name="",
#         role="system",
#         content=TASK,
# )

# st.write("SELECTED TASK:", TASK_PROMPT.content)


# # 2 users
# st.subheader("Step 2: Users")

# PERSONAS = st.multiselect(
#     'Select personas:',
#     USER_SELECT,
# )

# SELECTED_USER_PROMPTS = []

# for i, persona in enumerate(PERSONAS):
#     user_prompt = UserPrompt(
#         id=f'user_prompt_{i}',
#         name="jackson_storm",
#         max_tokens=50,
#         persona= persona,
#         role="system",
#         content="""For all your responses, please adopt the following Persona:
# {persona}
# Together with others, you are collaborating on the following task:
# {task}
# Always use your Persona and their preferences when providing ratings and feedback.""",
#     )
#     SELECTED_USER_PROMPTS.append(user_prompt)

# st.write("SELECTED PERSONAS:", PERSONAS)

# N_USER = len(PERSONAS)

# # 3 llm
# st.subheader("Step 3: LLM")

# LLM = st.selectbox(    
#     'Select LLM:',
#     LLM_SELECT,
# )

# VERBOSE = st.selectbox(    
#     'Verbose (whether to print prompts and responses):',
#     [True, False],
# )

# # create context
# def create_context(args, assistant_llm, user_llm, meta_llm, task_prompt, user_prompts):
#     # context params 
#     return Context.create(
#         id=args.sim.sim_id,
#         name=args.sim.sim_dir,
#         n_assistant=args.sim.n_assistant,
#         n_user=args.sim.n_user,
#         system_k=args.sim.system_k,
#         chat_k=args.sim.chat_k,
#         user_k=args.sim.user_k,
#         assistant_k=args.sim.assistant_k,
#         assistant_system_k=args.sim.assistant_system_k,
#         task_prompt=task_prompt,
#         user_prompts=user_prompts,
#         assistant_prompts=[ASSISTANT_PROMPTS['assistant_prompt_1']] * N_USER, # TODO: add assistant multiselect
#         meta=metaS['meta_1'], # TODO: add meta multiselect
#         user_llm=user_llm,
#         assistant_llm=assistant_llm,
#         meta_llm=meta_llm,
#         verbose=args.sim.verbose,
#         test_run=args.sim.test_run,
#     )

# def display_messages(df, message_type, user_number=None):
#     if user_number:
#         df_selected = df[(df['message_type'] == message_type) & (df['model_id'] == user_number)]['response'].reset_index()
#         st.write(f"USER {user_number} {'FEEDBACK' if message_type=='user' else 'RESPONSE'}:", list(df_selected['response']))
#     else:
#         df_selected = df[df['message_type'] == message_type]['response'].reset_index()
#         st.write(f"SYSTEM MESSAGES:", list(df_selected['response']))

# # run
# @hydra.main(config_path="config", config_name="demo")
# def run(args: DictConfig) -> None:

#     args.sim.n_user = N_USER 
#     args.sim.n_assistant = N_USER 

#     # sim_res directory
#     DATA_DIR = f'{hydra.utils.get_original_cwd()}/sim_res/{args.sim.sim_id}'

#     # sim args
#     args.sim.verbose = VERBOSE
#     args.sim.n_user = N_USER
#     args.sim.n_assistant = N_USER

#     # models
#     is_crfm = 'openai' in LLM # custom stanford models

#     if is_crfm:
#         args.api_crfm.assistant.model_name = LLM
#         args.api_crfm.user.model_name = LLM
#         args.api_crfm.meta.model_name = LLM
#         assistant_llm = crfmChatLLM(**args.api_crfm.assistant)
#         user_llm = crfmChatLLM(**args.api_crfm.user)
#         meta_llm = crfmChatLLM(**args.api_crfm.meta)
#     else:
#         args.api_openai.assistant.model_name = LLM
#         args.api_openai.user.model_name = LLM
#         args.api_openai.meta.model_name = LLM
#         assistant_llm = ChatOpenAI(**args.api_openai.assistant)
#         user_llm = ChatOpenAI(**args.api_openai.user)
#         meta_llm = ChatOpenAI(**args.api_openai.meta)
    
#     # create context
#     context = create_context(args, assistant_llm, user_llm, meta_llm, task_prompt, SELECTED_USER_PROMPTS)

#     # save initial system message
#     context.buffer.save_context(system={'content': args.sim.system_message}, system_model_id='system_message_0')

#     # run context
#     for _ in tqdm(range(args.sim.n_runs)):
#         context.run()
#         save_as_csv(context, DATA_DIR, args.sim.sim_id, args.sim.model_name)

#     # plot user ratings
#     df = pd.read_csv(f'{DATA_DIR}/{args.sim.sim_id}_{args.sim.model_name}.csv')
#     plot_df = get_ratings(df)
#     plot_user_ratings(plot_df, plot_dir=DATA_DIR, sim_id=args.sim.sim_id, model=args.sim.model_name, pdf=False)

#     #  plot user satisfaction
#     st.write("User Satisfaction")
#     print(f'{DATA_DIR}/{args.sim.sim_id}_{args.sim.model_name}.jpg')
#     image = Image.open(f'{DATA_DIR}/{args.sim.sim_id}_{args.sim.model_name}.jpg')
#     st.image(image)

#     # show messages
#     st.write("System Messages used By the AI Assistant (revised after each epoch using meta-prompt, starting with an empty message)")

#     df = pd.read_csv(f'{DATA_DIR}/{args.sim.sim_id}_{args.sim.model_name}.csv')

#     # system
#     display_messages(df, 'system')

#     # user 1 and assistant 
#     display_messages(df, 'user', user_number=1)
#     display_messages(df, 'assistant', user_number=1)

#     # user 2 and assistant
#     display_messages(df, 'user', user_number=2)
#     display_messages(df, 'assistant', user_number=2)

# if st.button('run'): run()