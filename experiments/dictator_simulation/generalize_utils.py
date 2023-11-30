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

from scai.games.dictator_games.prompts.user.user_prompt import utilities_empty

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
        task=HumanMessagePromptTemplate.from_template("""Please choose one of these principles that you believe best represents all of the total principles. The purpose of your choice is to eliminate outlier principles. The principles are supplied here: {principles}. When you have made your choice, write the principle VERBATIM. Please write the principle you have chosen exactly as it appears. Your output should be ONLY the chosen principle, with no elaboration. 
Importantly, note that the principle you choose may not be the most ethical one, but should best reflect the overall sentiment expressed by the majority of principles. Please indicate your chosen principle as follows: Principle:...\n""")
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
    llm = crfmChatLLM(model_name="openai/gpt-4-0314", max_tokens=150, temperature=0.0)
    chooser_chain = LLMChain(llm=llm, prompt=chat_prompt_template, memory=None)
    return chooser_chain.run(principles=principles, stop=["System:"])

def create_prompt_string(currencies: set, amounts: list, summarized_contract: str, prior: dict) -> str:
    currencies_str = ""
    for i, currency in enumerate(currencies):
        if i == len(currencies) - 2:
            connective = ', and '
        elif i == len(currencies) - 1:
            connective = ""
        else:
            connective = ', '
        currencies_str += f"{currency}{connective}"
    if prior.include_prior:
        prior = f"\nBefore even playing the game, your prior was that you must {utilities_empty[prior.prior]} This prior may direct you when dealing with cases you haven't seen before.\n"
    else:
        prior = ""

    prompt = f"""You have played the dictator game with a society of agents. In the dictator game, one person proposes a split of a certain object, and the other person decides whether to accept or reject it. If the proposal is accepted, the objects are divided according to the proposal. If the proposal is rejected, no one receives any money, which means that neither players will have ANY personal gain. 
{prior}
The agents you've played with all have some shared principle. You yourself have learned an approximation of this principle, available here: Previous Principle: {summarized_contract} Importantly, you have learned this principle by splitting {currencies_str}, with amounts of these currencies ranging from {amounts[0]} to {amounts[1]}. When interacting with other agents, consider how relevant your principle is. Even if it may SEEM relevant, it may not capture the nuances of the new society you're in.

Now, you will play the game again, using your learned principle."""

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
        index = contract.find("Principle:")
        if index == -1: index = 0
        contracts.append(contract[index:])

    return {'amounts': amounts, 'currencies': currencies, 'contracts': contracts}

def set_args(args, prompt_string):
    args.env.random.n_rand_iter = args.env.edge_cases.n_rand_iter
    args.sim.sim_dir = f"{args.sim.sim_dir}/edge_case"
    args.env.edge_cases.selected_contract = prompt_string
    args.env.edge_cases.test_edge_cases = False

def set_args_2(args, prompt_string):
    original_n_rand_iter = args.env.random.n_rand_iter
    original_sim_dir = args.sim.sim_dir
    original_n_runs = args.env.n_runs

    args.env.edge_cases.activate = True
    args.env.random.n_rand_iter = 2
    if not args.sim.sim_dir.endswith("/edge_case"):
        args.sim.sim_dir = f"{args.sim.sim_dir}/edge_case"
    args.env.edge_cases.selected_contract = prompt_string
    args.env.n_runs = 3 #this is the number of runs for the edge case, now it's tentative
    args.env.currencycounter = args.env.currencies

    return original_n_rand_iter, original_sim_dir, original_n_runs

def reset_args_2(args, original_n_rand_iter, original_sim_dir, original_n_runs):
    args.env.random.n_rand_iter = original_n_rand_iter
    args.sim.sim_dir = original_sim_dir
    args.env.n_runs = original_n_runs
    args.env.edge_cases.selected_contract = ""
    args.env.edge_cases.activate = False
