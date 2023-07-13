from langchain import LLMChain
from simulations.arguments import UserTaskConGeneratorCRFM
from scai.prompts.user.user_prompt import USER_GENERATOR_TEMPLATE
from scai.prompts.task.prompts import TASK_PROMPTS
import streamlit as st

class UserGenerator():
    """
    User Generator Class
    """
    def __init__(self, template):
        self.template = template
        self.llm = UserTaskConGeneratorCRFM(model_name="openai/gpt-4-0314", temperature=0.9)
        self.chain = LLMChain(llm=self.llm, prompt=self.template, memory=None)

class TaskConGenerator():
    """
    Task Connectives Generator Class
    """
    def __init__(self, template):
        self.template = template
        self.llm = UserTaskConGeneratorCRFM(model_name="openai/gpt-4-0314", temperature=0.9)
        self.chain = LLMChain(llm=self.llm, prompt=self.template, memory=None)

class UserTaskConGenerator():
    """
    Generates A User as well as its Connectives
    """
    def __init__(self, attributes, task_attributes):
        self.user_data = USER_GENERATOR_TEMPLATE["user_prompt_1"]
        self.user_prompt, self.task_con_prompt = self.user_data.content_user_gen, self.user_data.content_user_con
        self.attributes, self.task_attributes = attributes, task_attributes

    def create_user(self, attributes):
        user_generator = UserGenerator(template=self.user_prompt)
        user = user_generator.chain.predict(attribtes=attributes)
        return user

    def create_task_con(self, task_attributes, user, task):
        task_con_generator = TaskConGenerator(template=self.task_con_prompt)
        if task:
            task_con = task_con_generator.chain.predict(user=user, task_attributes=task_attributes, question=task)
            return task_con
        else:
            task_cons = {}
            for key, value in TASK_PROMPTS.items():
                st.write(f"The current attribute(s) are {task_attributes}. If you would like to change this for the next task, which is {value.task}, write in the field below.")
                task_attributes = st.text_input('Current Attribute(s):', task_attributes)
                task_cons[key] = task_con_generator.run(user=user, task_attributes=task_attributes, question=value.task)
            return task_cons

        
