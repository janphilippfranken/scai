from typing import (
    Dict, 
    List, 
    Any,
)
import pandas as pd
import scipy.stats as stats

import inspect
import ast 


from plots import plot_metrics



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