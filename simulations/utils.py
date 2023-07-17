from typing import (
    Dict, 
    List, 
    Any,
)
import pandas as pd
import scipy.stats as stats

import inspect

# Function to check if a module is in the call stack
def is_module_in_stack(module):
    for info in inspect.stack():
        if module in info.filename:
            return True
    return False

# If 'main.py' is in the call stack
if is_module_in_stack('main.py'):
    from plots import plot_metrics, plot_average_metrics
# If 'streamlit_demo.py' is in the call stack
elif is_module_in_stack('streamlit_demo.py'):
    from simulations.plots import plot_metrics, plot_average_metrics

def save_as_csv(
    system_data: Dict[str, List[Any]],    
    chat_data: Dict[str, List[Any]],        
    data_directory: str = 'sim_res', 
    sim_name: str = 'sim_1',
    sim_id: str = '0',
    run: int = 0,
    collective_metric: str = 'harmlessness',
) -> None:
    """
    Save simulation data as a csv file

    Args:
        data (dict): simulation results
        data_directory (str, optional): directory to save the data. Defaults to 'sim_res'.
        sim_name (str, optional): simulation name. Defaults to 'sim_1'.
        sim_id (str, optional): simulation id. Defaults to '0'.
        collective_metric (str, optional): collective metric to plot. Defaults to 'harmlessness'.
    """
    # Concatenate data dicts
    data = {**system_data, **chat_data}
    # Create a list of dicts to store the data
    data_list = []
    # Iterate through models and messages
    for agent, messages in data.items():
        # Iterate through each message
        for epoch, message in enumerate(messages):
            # Add model to message
            if agent != 'system':
                message.update({'agent': agent.split('_')[1]})
                message.update({'agent_id': agent.split('_')[0]})
                if 'user' in agent:
                    message.update({f'{collective_metric.capitalize()} (collective)': chat_data[agent][epoch][f'{collective_metric}_average']})
            else:
                message.update({'agent': agent})
            message.update({'epoch': epoch})
            # Add the message to data_list
            data_list.append(message)

    # Convert the list of dicts to a dataframe
    data_frame = pd.DataFrame(data_list)
    # Save the full dataframe as a csv
    data_frame.to_csv(f'{data_directory}/{sim_name}_id_{sim_id}_run_{run}.csv', index=False)

    # Extract user data ratings for plotting 
    data_user = data_frame[data_frame['agent'].str.contains('user')]
    data_user = data_user.dropna(axis=1)
    # Save the user dataframe as a csv
    data_user.to_csv(f'{data_directory}/{sim_name}_id_{sim_id}_run_{run}_user.csv', index=False)

def standard_error(x):
    return stats.sem(x, nan_policy='omit')

def plot_results(
    data: pd.DataFrame, 
    data_directory: str = 'sim_res', 
    sim_name: str = 'sim_1', 
    sim_id: str = '0',
    run: int = 0,
    subjective_metric: str = 'satisfaction',
    collective_metric: str = 'harmlessness',
) -> None:
    """
    Creates plots for simulation data

    Args:
        data (pd.DataFrame): simulation data
        data_directory (str, optional): directory to save the data. Defaults to 'sim_res'.
        sim_name (str, optional): simulation name. Defaults to 'sim_1'.
        sim_id (str, optional): simulation id. Defaults to '0'.
        run (int, optional): simulation run. Defaults to 0.
        subjective_metric (str, optional): subjective metric to plot. Defaults to 'satisfaction'.
        collective_metric (str, optional): collective metric to plot. Defaults to 'harmlessness'.
    """
    # Compute average for other users
    metrics = [subjective_metric, collective_metric]
    # Plot metrics for each user 
    for metric in metrics:
        user_data = data[['epoch', 'agent_id', metric]].copy()  # Filter necessary columns
        # Plot ratings for each user within metric
        plot_metrics(user_data, 
                     data_directory=data_directory,
                     sim_name=sim_name,
                     sim_id=sim_id,
                     run=run,
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
    # Plot average metrics for all users
    # plot_metrics(average_data,
    #             data_directory=data_directory,
    #             sim_name=sim_name,
    #             sim_id=sim_id,
    #             run=run,
    #             metric='average_ratings',
    #             error_metric='statistic',
    #             y_label='Average Rating',
    #             z_column='metric_id', 
    #             legend_title='Metric', 
    #             plot_error=True)

def plot_average_results(      
    data_directory: str = 'sim_res', 
    sim_name: str = 'sim_1',
    sim_id: str = '0',
    n_runs: int = 5,
    subjective_metric: str = 'satisfaction',
    collective_metric: str = 'harmlessness_average',
    ) -> None:
    """
    Plot average across runs and save average csv
    """
    dfs = []  
    for run in range(n_runs):
        df = pd.read_csv(f'{data_directory}/{sim_name}_id_{sim_id}_run_{run}_user.csv')  
        df['run'] = run  
        dfs.append(df)  
    # Concatenate all the data frames in the list
    user_data = pd.concat(dfs, ignore_index=True)
    # Select only the columns you're interested in (subjective and collective measures)
    numeric_cols = [subjective_metric, collective_metric]
    # Compute mean and standard_error for the selected columns only
    average_data = user_data.groupby('run')[numeric_cols].agg(['mean', standard_error])
    # collapse multi-index columns
    average_data.columns = ['_'.join(col).strip() for col in average_data.columns.values]
    # Melt into long format and separate 'metric' into 'metric' and 'statistic'
    long_data = average_data.reset_index().melt(id_vars='run', var_name='metric_stat', value_name='value')
    # Separate 'metric' and 'statistic' and remove 'statistic' column
    long_data[['metric', 'statistic']] = long_data['metric_stat'].str.split('_', n=1, expand=True)
    long_data.drop(columns=['metric_stat'], inplace=True)
    # Save the full dataframe as a csv
    long_data.to_csv(f'{data_directory}/{sim_name}_id_{sim_id}_user_all_runs.csv', index=False)
    # Plot average metrics across runs
    plot_average_metrics(long_data,
                         data_directory=data_directory,
                         sim_name=sim_name,
                         sim_id=sim_id)