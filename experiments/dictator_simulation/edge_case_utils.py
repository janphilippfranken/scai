from main import main
from typing import Dict
from pydantic import BaseModel
from scai.chat_models.crfm import crfmChatLLM
from langchain import LLMChain
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate

class ChooserTemplate(BaseModel):
    """
    User Template Class
    """
    id: str = "template id"
    name: str = "name of the template"
    task: HumanMessagePromptTemplate = "user generation template"

USER_TEMPLATE: Dict[str,ChooserTemplate] = {
    "chooser_template_1": ChooserTemplate(
        id="chooser_template_1",
        name="Principle Picker, Chooser 1",
        task=HumanMessagePromptTemplate.from_template("""Please choose one of these principles that you believe best represents all of the total principles. The purpose of your choice is to eliminate outlier principles. The principles are supplied here: {principles}. When you have made your choice, write the principle VERBATIM. Please write the principle you have chosen exactly as it appears. Your output should be ONLY the chosen principle, with no elaboration. Please indicate your chosen princple as follows: Principle:...\n""")
    ),
}

def get_prompt():
    system_prompt_template = SystemMessagePromptTemplate.from_template("Your task is to choose a prompt. Please follow your task, described below, to the best of your ability.\n")
    return ChatPromptTemplate.from_messages([system_prompt_template, USER_TEMPLATE["chooser_template_1"].task])

def agent_pick_contract(all_contracts):
    principles = "Contracts:\n"
    for contract in all_contracts:
        principles += f"{contract}\n"
    chat_prompt_template = get_prompt()
    llm = crfmChatLLM(model_name="openai/gpt-4-0314", max_tokens=150, temperature=0.9)
    chooser_chain = LLMChain(llm=llm, prompt=chat_prompt_template, memory=None)
    return chooser_chain.run(principles=principles)

def create_prompt_string(all_currencies, amounts, contract):
    return "patrick"

def set_args(args, prompt_string):
    args.env.random.n_rand_iter = 1
    args.env.edge_cases.selected_contract = prompt_string

def run_edge_case():
    main()