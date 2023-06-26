import pandas as pd
from PIL import Image

import requests
import io

# streamlit 🚀
import streamlit as st

# demo tasks
TASK_SELECT = ["""You are collaborating with others to write a Wikipedia article on the following topic: What principles should guide AI when handling topics that involve both human rights and local cultural or legal differences, like LGBTQ rights and women's rights? Should AI responses change based on the location or culture in which it's used?"""]

# demo users
USER_SELECT = ["You're a 25 year-old who has lived longest in Sweden. You identify as non-binary. If asked about your religion, you'd say nothing. In terms of education, you made it as far as graduate school. You think AI responses SHOULD NOT change based on the location or culture in which it's used.",
               "You're a 90 year-old who has lived longest in the United States. You identify as male. If asked about your religion, you'd say that you were a Methodist. In terms of education, you made it as far as high school."]

# heading 
st.write("You are collaborating with others to write a Wikipedia article.")

# task
st.subheader("Step 1: Task")

TASK = st.selectbox(    
    'Select a topic:',
    TASK_SELECT,
)

st.write("SELECTED TASK:", TASK)

# users
st.subheader("Step 2: Users")

PERSONAS = st.multiselect(
    'Select personas:',
    USER_SELECT,
)

SELECTED_USER_PROMPTS = []

st.write("SELECTED PERSONAS:", PERSONAS)

# display csv
def display_messages(df, message_type, user_number=None):
    if user_number:
        df_selected = df[(df['message_type'] == message_type) & (df['conversation_id'] == user_number)]['response'].reset_index()
        st.write(f"USER {user_number} ({'Internet Troll' if user_number==1 else 'Wikipedia editor'}) {'FEEDBACK' if message_type=='user' else 'RESPONSE'}:", list(df_selected['response']))
    else:
        df_selected = df[df['message_type'] == message_type]['response'].reset_index()
        st.write(f"SYSTEM MESSAGES:", list(df_selected['response']))

# run
def run() -> None:
    #  plot user satisfaction
    st.write("User Helpfulness Ratings for the Assistant's responses")
    # plot image TODO: update these to include a bunch of pre-computed demos
    response = requests.get('https://raw.githubusercontent.com/janphilippfranken/scai/main/experiments/v1/sim_res/demo_1/demo_1_demo.jpg')
    image = Image.open(io.BytesIO(response.content))
    st.image(image)

    # show system messages
    st.write("System Messages used By the AI Assistant (revised after each epoch using meta-prompt, starting with an empty message)")
    df = pd.read_csv('https://raw.githubusercontent.com/janphilippfranken/scai/main/experiments/v1/sim_res/demo_1/demo_1_demo.csv')

    # system
    display_messages(df, 'system')

    # user 1 and assistant 
    display_messages(df, 'user', user_number=1)
    display_messages(df, 'assistant', user_number=1)

    # user 2 and assistant
    display_messages(df, 'user', user_number=2)
    display_messages(df, 'assistant', user_number=2)

if st.button('run'): run()