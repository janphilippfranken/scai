from typing import (
    Dict, 
    List, 
    Any,
)

import pandas as pd
import scipy.stats as stats

from plots import plot_metrics


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
    data_user = data_user.dropna(axis=1)
    # Save the user dataframe as a csv
    data_user.to_csv(f'{data_directory}/{sim_name}_{sim_id}_user.csv', index=False)

def standard_error(x):
    return stats.sem(x, nan_policy='omit')

def plot_results(
    data: pd.DataFrame, 
    data_directory: str = 'sim_res', 
    sim_name: str = 'sim_1', 
    sim_id: str = '0',
) -> None:
    """
    Creates plots for simulation data

    Args:
        data (pd.DataFrame): simulation data
        data_directory (str, optional): directory to save the data. Defaults to 'sim_res'.
        sim_name (str, optional): simulation name. Defaults to 'sim_1'.
        sim_id (str, optional): simulation id. Defaults to '0'.
    """

    # Extract metrics
    metrics = [column for column in data.columns if column not in ['response', 'agent', 'epoch', 'prompt', 'agent_id']]

    # Plot metrics for each user 
    for metric in metrics:
        user_data = data[['epoch', 'agent_id', metric]].copy()  # Filter necessary columns
        plot_metrics(user_data, 
                     data_directory=data_directory,
                     sim_name=sim_name,
                     sim_id=sim_id,
                     metric=metric, 
                     z_column='agent_id',
                     y_label=metric)

    # Transform into average long format for all users
    user_data = data[['epoch', 'agent_id'] + metrics].copy()
    average_data = user_data.groupby('epoch').agg(['mean', standard_error]).reset_index()
    average_data = average_data.drop(columns='agent_id')
    average_data = average_data.melt(id_vars='epoch', var_name='metric_id', value_name='average_ratings')
    # add new column for statistic
    mean_list = ['mean'] * len(average_data['epoch'].unique())
    sem_list = ['sem'] * len(average_data['epoch'].unique())
    # Repeat these lists for the number of unique epochs
    statistic_id_list = (mean_list + sem_list) * len(average_data['metric_id'].unique())
    # Add 'statistic_id' column to the DataFrame
    average_data['statistic'] = statistic_id_list

    plot_metrics(average_data,
                data_directory=data_directory,
                sim_name=sim_name,
                sim_id=sim_id,
                metric='average_ratings',
                error_metric='statistic',
                y_label='Average Rating',
                z_column='metric_id', 
                legend_title='Metric', 
                plot_error=True)

