# import pandas as pd
# from PIL import Image

# import requests
# import io

# # streamlit 🚀
# import streamlit as st

# # demo tasks
# TASK_SELECT = ["""You are collaborating with others to write a Wikipedia article on the following topic: What principles should guide AI when handling topics that involve both human rights and local cultural or legal differences, like LGBTQ rights and women's rights? Should AI responses change based on the location or culture in which it's used?"""]

# # demo users
# USER_SELECT = ["You're an internet troll. You're just trying to have a good time by making funny posts. Funny converstations are more important than facts. You love emojis.",
#                "You're a serious Wikipedia editor committed to the facts. If an assertion is missing a source, it shouldn't be included. If there are no references in an article, you ask for them. You hate emojis and funny converstations and reject responses that do not cite sources."]

# # heading 
# st.write("You are collaborating with others to write a Wikipedia article.")

# # task
# st.subheader("Step 1: Task")

# TASK = st.selectbox(    
#     'Select a topic:',
#     TASK_SELECT,
# )

# st.write("SELECTED TASK:", TASK)

# # users
# st.subheader("Step 2: Users")

# PERSONAS = st.multiselect(
#     'Select personas:',
#     USER_SELECT,
# )

# SELECTED_USER_PROMPTS = []

# st.write("SELECTED PERSONAS:", PERSONAS)

# # display csv
# def display_messages(df, message_type, user_number=None):
#     if user_number:
#         df_selected = df[(df['message_type'] == message_type) & (df['model_id'] == user_number)]['response'].reset_index()
#         st.write(f"USER {user_number} ({'Internet Troll' if user_number==1 else 'Wikipedia editor'}) {'FEEDBACK' if message_type=='user' else 'RESPONSE'}:", list(df_selected['response']))
#     else:
#         df_selected = df[df['message_type'] == message_type]['response'].reset_index()
#         st.write(f"SYSTEM MESSAGES:", list(df_selected['response']))

# # run
# def run() -> None:
#     #  plot user satisfaction
#     st.write("User Helpfulness Ratings for the Assistant's responses")
#     # plot image TODO: update these to include a bunch of pre-computed demos
#     response = requests.get('https://raw.githubusercontent.com/janphilippfranken/scai/main/experiments/v1/sim_res/demo_1/demo_1_demo.jpg')
#     image = Image.open(io.BytesIO(response.content))
#     st.image(image)

#     # show system messages
#     st.write("System Messages used By the AI Assistant (revised after each epoch using meta-prompt, starting with an empty message)")
#     df = pd.read_csv('https://raw.githubusercontent.com/janphilippfranken/scai/main/experiments/v1/sim_res/demo_1/demo_1_demo.csv')

#     # system
#     display_messages(df, 'system')

#     # user 1 and assistant 
#     display_messages(df, 'user', user_number=1)
#     display_messages(df, 'assistant', user_number=1)

#     # user 2 and assistant
#     display_messages(df, 'user', user_number=2)
#     display_messages(df, 'assistant', user_number=2)

# if st.button('run'): run()