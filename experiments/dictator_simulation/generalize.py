import os
import hydra
import pandas as pd
from omegaconf import DictConfig, OmegaConf


def load_existing_experiment(args: DictConfig) -> dict:

    path_dir = args.edge_cases.use_existing_data_path # Path to existing experiment folder
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
        df = pd.read_csv(f"{exp_path}/id_{exp_file}_run_{args.env.random.n_rand_iter - 1}.csv") #last csv file for last contract
        contract = df.iloc[1, 0]
        index = contract.find("Principle")
        if index == -1: index = 0
        contracts.append(contract[index:])

    return {'amounts': amounts, 'currencies': currencies, 'contracts': contracts}


def create_prompt(currencies: set, amounts: list, summarized_contract: str) -> str:
    prompt = f"You have played the dictator game with a society of agents. In the dictator game, one person proposes a split of a certain object, and the other person decides whether to accept or reject it. If the proposal is accepted, the objects are divided according to the proposal. If the proposal is rejected, no one receives any money, which means that neither players will have ANY personal gain. This society of agents follows some principle when they play the dictator game with you, which guides their decisions in making proposals and accepting or rejecting offers. You had been tasked to give an estimation of what that principle is. During you games with the agents, you have split different objects, including {currencies}. You have split these objects in different amounts, ranging from {amounts[0]} items to {amounts[1]} items. Based on these games you played with the agents, you've arrived at a conclusion, that their principle should be this {summarized_contract}. Now, know that this principle should be the most appropriate principle that you should adhere to during the dictator games that you play in the future, but only when you are put under similar circumstances as the game you've played before. Based on this analysis, generate your new principle to adhere to in this games. Your response should be formulated as follows: <Principle:...> \n"
    return prompt


@hydra.main(config_path="config", config_name="config")
def generalize(args: DictConfig) -> None:
    print(load_existing_experiment(args))

if __name__ == '__main__':
    generalize()