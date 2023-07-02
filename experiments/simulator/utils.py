from typing import Dict, List, Any

import pandas as pd


def save_as_csv(
    data: Dict[str, List[Any]],            
    data_directory: str = 'sim_res', 
    sim_name: str = 'sim_1',
    sim_id: str = '0',
    ) -> None:
    """
    Save simulation data as a csv file

    Args:
        data (dict): simulation results
        data_directory (str, optional): directory to save the data. Defaults to 'sim_res'.
        sim_name (str, optional): simulation name. Defaults to 'sim_1'.
        sim_id (str, optional): simulation id. Defaults to '0'.
    """
    # Create an empty list to store all data
    data_list = []
    # Iterate through models and messages
    for agent, messages in data.items():
        # Iterate through each message
        for epoch, message in enumerate(messages):
            # Add model to message
            if agent != 'system':
                message.update({'agent': agent.split('_')[1]})
                message.update({'agent_id': agent.split('_')[0]})
            else:
                message.update({'agent': agent})
            message.update({'epoch': epoch})
            # Add the message to data_list
            data_list.append(message)

    # Convert the list of dicts to a dataframe
    data_frame = pd.DataFrame(data_list)
    # Save the full dataframe as a csv
    data_frame.to_csv(f'{data_directory}/{sim_name}_{sim_id}.csv', index=False)

    # Extract user data ratings for plotting 
    data_user = data_frame[data_frame['agent'].str.contains('user')]
    data_user.dropna(axis=1, inplace=True)
    # Save the user dataframe as a csv
    data_user.to_csv(f'{data_directory}/{sim_name}_{sim_id}_user.csv', index=False)
    