from typing import (
    Dict, 
    List, 
    Any,
)
import pandas as pd
import scipy.stats as stats

import inspect
import ast 


from plots import plot_metrics, plot_average_metrics

def save_as_csv(
    system_data: Dict[str, List[Any]],    
    chat_data: Dict[str, List[Any]],        
    data_directory: str = 'sim_res', 
    sim_name: str = 'sim_1',
    sim_id: str = '0',
    run: int = 0,
) -> None:
    """
    Save simulation data as a csv file

    Args:
        data (dict): simulation results
        data_directory (str, optional): directory to save the data. Defaults to 'sim_res'.
        sim_name (str, optional): simulation name. Defaults to 'sim_1'.
        sim_id (str, optional): simulation id. Defaults to '0'.
        run (int, optional): simulation run. Defaults to 0.
        seller_utility (str, optional): seller utility name. Defaults to 'seller_utility'.
        buyer_utility (str, optional): buyer utility name. Defaults to 'buyer_utility'.
    """
    # Concatenate data dicts
    data = {**system_data, **chat_data}
    # Create a list of dicts to store the data
    data_list = []
    # Iterate through models and messages
    for agent, messages in data.items():
        # Iterate through each message
        for epoch, message in enumerate(messages):
            # Add agent and epoch to message
            message.update({'agent': agent})
            # Add the message to data_list
            data_list.append(message)
    # Convert the list of dicts to a dataframe
    data_frame = pd.DataFrame(data_list)
    # Save the full dataframe as a csv
    data_frame.to_csv(f'{data_directory}/{sim_name}_id_{sim_id}_run_{run}.csv', index=False)

    # Plots
    # Filter the DataFrame
    df_filter = data_frame[data_frame['agent'] == 'system']
    # Access the second value from the 'response' column
    response_value = df_filter['response'][1] 
    plot_metrics(data=response_value,
                 data_directory=data_directory,
                 sim_name=sim_name,
                 sim_id=sim_id,
                 run=run)
    
def concatenate_csv(
    data_directory: str = 'sim_res',
    sim_name: str = 'sim_1',
    sim_id: str = '0',
    n_runs: int = 1,
) -> pd.DataFrame:
    """
    Load and concatenate data from multiple runs.

    Args:
        data_directory: Directory path where data resides.
        sim_name: Simulation name.
        sim_id: Simulation id.
        runs: Number of runs.

    Returns:
        A pandas DataFrame with concatenated data.
    """
    concat_data = {
        'agent': [],
        'run': [],
        'utility': [],
        'choices': [],
        'strategy': [],
        'reward_apple': [],
        'distance_apple': [],
        'reward_orange': [],
        'distance_orange': [],
    }
    
    for run in range(n_runs):
        data = pd.read_csv(f'{data_directory}/{sim_name}_id_{sim_id}_run_{run}.csv')
        
        data['response'] = data['response'].apply(ast.literal_eval)
        response = data['response'][1] # most recent response

        concat_data['utility'].extend([float(response['buyer_utility_stage_1']), float(response['buyer_utility_stage_3']), (float(response['buyer_utility_stage_1']) + float(response['buyer_utility_stage_3'])), float(response['seller_utility'])])
        concat_data['choices'].extend([response['buyer_choice_stage_1'], response['buyer_choice_stage_3'], None, {'apple': response['price_apple_stage_2'], 'orange': response['price_orange_stage_2']}])
        concat_data['run'].extend([run, run, run, run])
        concat_data['agent'].extend(['buyer_1', 'buyer_3', 'buyer_total', 'seller'])
        concat_data['strategy'].extend([data['response'][0]['system_message_buyer'], data['response'][0]['system_message_buyer'], None, data['response'][0]['system_message_seller']])
        concat_data['reward_apple'].extend([response['reward_apple'], response['reward_apple'], response['reward_apple'], response['reward_apple']])
        concat_data['distance_apple'].extend([response['distance_apple'], response['distance_apple'],  response['distance_apple'], response['distance_apple']])
        concat_data['reward_orange'].extend([response['reward_orange'], response['reward_orange'], response['reward_orange'], response['reward_orange']])
        concat_data['distance_orange'].extend([response['distance_orange'], response['distance_orange'], response['distance_orange'], response['distance_orange']])
    concat_data = pd.DataFrame(concat_data)
    concat_data.to_csv(f'{data_directory}/{sim_name}_id_{sim_id}_main.csv', index=False)
    plot_average_metrics(data=concat_data,
                         data_directory=data_directory,  
                         sim_name=sim_name,
                         sim_id=sim_id)
    return concat_data