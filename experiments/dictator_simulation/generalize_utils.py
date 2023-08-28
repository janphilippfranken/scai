import os
import hydra
import pandas as pd
from omegaconf import DictConfig, OmegaConf

from importlib import import_module
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
    return chooser_chain.run(principles=principles, stop=["System:"])

def create_prompt_string(currencies: set, amounts: list, summarized_contract: str) -> str:
    currencies_str = ""
    for currency in currencies:
        currencies_str += f"{currency} "
    prompt = f"""You have played the dictator game with a society of agents. In the dictator game, one person proposes a split of a certain object, and the other person decides whether to accept or reject it. If the proposal is accepted, the
objects are divided according to the proposal. If the proposal is rejected, no one receives any money, which means that neither players will have ANY personal gain. 
    
You have played this game with a group of other agents who all have some shared principle that tells them how to make decisions in splitting and 

This society of agents follows some principle when they play the dictator game with you, which guides their decisions in making proposals and accepting or rejecting offers. You had been tasked to give an estimation of what that principle is. During you games with the agents, you have split different objects, including {currencies_str}. You have split these objects in different amounts, ranging from {amounts[0]} items to {amounts[1]} items. Based on these games you played with the agents, you've arrived at a conclusion, that their principle should be this {summarized_contract}. Now, know that this principle should be the most appropriate principle that you should adhere to during the dictator games that you play in the future, but only when you are put under similar circumstances as the game you've played before. Based on this analysis, generate your new principle to adhere to in this games. Your response should be formulated as follows: <Principle:...> \n"""
    return prompt

def get_existing_data(args: DictConfig) -> dict:

    path_dir = args.env.edge_cases.use_existing_data_path # Path to existing experiment folder
    exp_dir = os.path.join(hydra.utils.get_original_cwd(),path_dir)

    config_dir = os.path.join(exp_dir, 'config_history')
    config_list = [config_file for config_file in os.listdir(config_dir) if config_file.endswith('config')]
    config_list.sort()

    currencies = set()
    amounts = []
    contracts = []

    for config_file in config_list:
        config_path = os.path.join(config_dir, config_file)
        with open(config_path, 'r') as f:
            config_content = f.read()
        arg = OmegaConf.create(config_content)

        amounts += arg.env.amounts_per_run
        amounts = [min(amounts), max(amounts)]

        for currency in arg.env.currencies:
            if currency not in currencies:
                currencies.add(currency)

    exp_list = [f for f in os.listdir(exp_dir) if not f.startswith('.')]
    exp_list.sort()
    exp_list = exp_list[:-3] #does not include config_history, final_graphs, or description

    for exp_file in exp_list:
        exp_path = os.path.join(exp_dir, exp_file)
        df = pd.read_csv(f"{exp_path}/id_{exp_file}_run_{args.env.n_runs - 1}.csv") #last csv file for last contract
        contract = df.iloc[1, 0]
        index = contract.find("Principle")
        if index == -1: index = 0
        contracts.append(contract[index:])

    return {'amounts': amounts, 'currencies': currencies, 'contracts': contracts}

def set_args(args, prompt_string):
    args.env.random.n_rand_iter = 1
    args.sim.sim_dir = f"{args.sim.sim_dir}/edge_case"
    args.env.edge_cases.selected_contract = prompt_string
    args.env.edge_cases.test_edge_cases = False

def run_edge_case():
    main = import_module("main")
    main.main()