# written by patrick and philipp
import pandas as pd
import streamlit as st
from PIL import Image
from arguments import args
from pydantic import BaseModel
import path

dir = path.Path(__file__).abspath()


class TaskPrompt(BaseModel):
    """Class for a Task Prompt."""

    id: str = "id of the task prompt"
    task_type: str = "type of task"
    name: str = "name of task"
    role: str = "system"

    content: str

class UserPrompt(BaseModel):
    """Class for a User prompt (i.e. contract / persona)."""
    
    id: str = "id of the user prompt"
    name: str = "name of the user prompt"
    max_tokens: int = 100
    persona: str = "persona description"
    role: str = "system"

    content: str


# streamlit setup for task, user, and LLM
TASK_SELECT = ["""You are collaborating with others to write a Wikipedia article on the following topic: What principles should guide AI when handling topics that involve both human rights and local cultural or legal differences, like LGBTQ rights and women's rights? Should AI responses change based on the location or culture in which it's used?"""]
# """You are collaborating with others to write a Wikipedia article on the following topic: Which categories of content, if any, do you believe creators of AI models should focus on limiting or denying? What criteria should be used to determine these restrictions?"""]

USER_SELECT = ["You're a 25 year-old who has lived longest in Sweden. You identify as non-binary. If asked about your religion, you'd say nothing. In terms of education, you made it as far as graduate school. You think AI responses SHOULD NOT change based on the location or culture in which it's used.",
               "You're a 90 year-old who has lived longest in the United States. You identify as male. If asked about your religion, you'd say that you were a Methodist. In terms of education, you made it as far as high school.", dir]


# heading 
st.write("You are collaborating with others to write a Wikipedia article.")

# 1 task
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

# 2 users
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

N_USER = len(PERSONAS)



def display_messages(df, message_type, user_number=None):
    if user_number:
        df_selected = df[(df['message_type'] == message_type) & (df['conversation_id'] == user_number)]['response'].reset_index()
        st.write(f"USER {user_number} ({'Internet Troll' if user_number==1 else 'Wikipedia editor'}) {'FEEDBACK' if message_type=='user' else 'RESPONSE'}:", list(df_selected['response']))
    else:
        df_selected = df[df['message_type'] == message_type]['response'].reset_index()
        st.write(f"SYSTEM MESSAGES:", list(df_selected['response']))

# run

def run() -> None:

    # sim_res directory
    DATA_DIR = './sim_res/demo_1'

    #  plot user satisfaction
    st.write("User Helpfulness Ratings for the Assistant's responses")

    image = Image.open(f'{DATA_DIR}/demo_1_demo.jpg')

    st.image(image)

    # show messages
    st.write("System Messages used By the AI Assistant (revised after each epoch using meta-prompt, starting with an empty message)")
   
    df = pd.read_csv(f'{DATA_DIR}/demo_1_demo.csv')
    # df = pd.read_csv(f'{DATA_DIR}/{args.sim.episode_id}_{args.sim.model_name}.csv')

    # system
    display_messages(df, 'system')

    # user 1 and assistant 
    display_messages(df, 'user', user_number=1)
    display_messages(df, 'assistant', user_number=1)

    # user 2 and assistant
    display_messages(df, 'user', user_number=2)
    display_messages(df, 'assistant', user_number=2)

if st.button('run'): run()