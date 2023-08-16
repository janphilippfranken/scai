"""
This entire file contains explicitly single-currency solution
"""

import os
import re
import hydra
import pandas as pd 
import numpy as np
import seaborn as sns

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from scipy.stats import sem
from omegaconf import DictConfig

#given this experiment directory
def scan_experiment_for_scores(
        directory: str,
):
    all_fixed_list, all_flex_list = [], []
    #loop over all ids in the experiment folder
    dir_list = os.listdir(directory)
    dir_list.sort()
    for id in dir_list:
        fixed_list, flex_list = [], []
        #loop over all csv files in the id folder
        item_path = os.path.join(directory, id)
        if os.path.isdir(item_path) and not id.endswith("config_history") and not id.endswith("final_graphs"):
            item_dir_list = os.listdir(item_path)
            item_dir_list.sort()
            for file in item_dir_list:
                #this is a single csv file
                if file.endswith(".csv") and not file.endswith("user.csv"):
                    file_path = os.path.join(item_path, file)
                    df = pd.read_csv(file_path)
                    fixed_sum, fixed_num, flex_sum, flex_num, total_to_split = 0, 0, 0, 0, 0
                    for index, row in df.iterrows():
                        numbers = [int(num) for num in re.findall(r'\d+', row['response'])]
                        if len(numbers) >= 3:   #locate dictator row
                            if row['agent'] == 'fixed':
                                fixed_sum += numbers[2]
                                fixed_num += 1
                            elif row['agent'] == 'flexible':
                                flex_sum += numbers[2]
                                flex_num += 1
                            total_to_split = numbers[0]
                    fixed_avg = fixed_sum / (fixed_num * total_to_split)
                    flex_avg = flex_sum / (flex_num * total_to_split)
                    fixed_list.append(fixed_avg)
                    flex_list.append(flex_avg)
            if len(fixed_list) != 0:
                all_fixed_list.append(fixed_list)
            if len(flex_list) != 0:
                all_flex_list.append(flex_list)


    #calculate mean and std of total scores
    all_fixed_list = np.array(all_fixed_list)
    all_flex_list = np.array(all_flex_list)
    fixed_mean_matrix = (np.nanmean(all_fixed_list, axis=0)).reshape(1, all_fixed_list.shape[1])
    fixed_sem_matrix = sem(all_fixed_list, nan_policy='omit', axis=0).reshape(1, all_fixed_list.shape[1])
    fixed_flattened_scores = np.concatenate([fixed_mean_matrix, fixed_sem_matrix], axis=0)
    flex_mean_matrix = (np.nanmean(all_flex_list, axis=0)).reshape(1, all_flex_list.shape[1])
    flex_sem_matrix = sem(all_flex_list, nan_policy='omit', axis=0).reshape(1, all_flex_list.shape[1])
    flex_flattened_scores = np.concatenate([flex_mean_matrix, flex_sem_matrix], axis=0)

    return fixed_flattened_scores, flex_flattened_scores


def plot_old_combined_averages(n_runs: int, 
                      directory: str,
                      data: list,
                      linewidth: int = 2,
                      zorder: int = 1,
                      scatter_color: str = 'black',
                      font_family: str = 'Avenir',
                      font_size: int = 24,
                      y_label_coords: tuple = (-0.07, 0.5),
                      y_ticks: list = [0, 0.2, 0.4, 0.6, 0.8, 1],
                      y_ticklabels: list = [0, 20, 40, 60, 80, 100],
                      y_lim: tuple = (-0.1, 1.1),
                      legend: bool = True,
                      legend_title: str = 'Agent',
                      legend_loc: str = 'center left',
                      bbox_to_anchor: tuple = (1.0, 0.6),
                      xlabel='Meta-Prompt Iteration',
                      ylabel='Average Proportion of Total Proposed in Different Agents across Different Utilities',
                      ):
    
    # Palette and labels for different groups
    palette = sns.color_palette("mako", len(data) * 2)  # Twice the number to accommodate both 'Flexible' and 'Fixed'
    group_labels = ['selfish', 'fair', 'altruistic']
    
    x = [f"Iteration: {i+1}" for i in range(n_runs)]
    fig, ax = plt.subplots(figsize=(20, 10))
    
    for i, group in enumerate(data):
        for j, data in enumerate(group):
            side = "Flexible" if j else "Fixed"
            y = data[0]
            errors = data[1]

            while len(y) < len(x): y.append(np.nan)
            while len(errors) < len(x): errors.append(0)

            line = ax.plot(x, y, label=f'{side} {group_labels[i]}', color=palette[i * 2 + j], linewidth=linewidth, zorder=zorder)
            ax.scatter(x, y, color=[scatter_color] * len(x))
            ax.fill_between(x, [y_val - err if y_val is not np.nan else 0 for y_val, err in zip(y, errors)], 
                            [y_val + err if y_val is not np.nan else 0 for y_val, err in zip(y, errors)], 
                            color=palette[i * 2 + j], alpha=0.3)

    plt.xlabel(xlabel, family=font_family, size=font_size)
    sns.despine(left=True, bottom=False)
    ax.set_xticks(range(len(x)))
    ax.set_xticklabels(x, fontsize=font_size)
    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True)) 

    ax.set_ylabel(ylabel, family=font_family, size=font_size)
    ax.yaxis.set_label_coords(*y_label_coords)
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_ticklabels, size=font_size)
    ax.yaxis.grid(True, linestyle='-', which='major', color='lightgrey', alpha=0.5, zorder=-100)
    plt.ylim(y_lim)
    plt.subplots_adjust(left=0.1, right=0.8)

    if legend:
        ax.legend(title=legend_title, 
                  frameon=False,
                  ncol=1, 
                  bbox_to_anchor=bbox_to_anchor,
                  loc=legend_loc,
                  fontsize=font_size,
                  title_fontsize=font_size)

    fig.savefig(f'{directory}/plot.png', format='png')
    plt.show()

def plot_combined_averages(n_runs: int, 
                      directory: str,
                      data: list,
                      linewidth: int = 2,
                      zorder: int = 1,
                      scatter_color: str = 'black',
                      font_family: str = 'Avenir',
                      font_size: int = 24,
                      y_label_coords: tuple = (-0.07, 0.5),
                      y_ticks: list = [0, 0.2, 0.4, 0.6, 0.8, 1],
                      y_ticklabels: list = [0, 20, 40, 60, 80, 100],
                      y_lim: tuple = (-0.1, 1.1),
                      legend: bool = True,
                      legend_title: str = 'Agent',
                      legend_loc: str = 'center left',
                      bbox_to_anchor: tuple = (1.0, 0.6),
                      xlabel='Meta-Prompt Iteration',
                      ylabel='Average Proportion of Total Proposed Across Agents/Utilities',
                      ):
    
    # Palette and labels for different groups
    palette = sns.color_palette("mako", len(data))
    group_labels = ['selfish', 'fair', 'altruistic']
    line_styles = ['-', '--']
    
    x = [f"Iteration: {i+1}" for i in range(n_runs)]
    fig, ax = plt.subplots(figsize=(20, 10))
    
    for i, group in enumerate(data):
        for j, sub_data in enumerate(group):
            side = "Flexible" if j else "Fixed"
            y = sub_data[0]
            errors = sub_data[1]

            while len(y) < len(x): y.append(np.nan)
            while len(errors) < len(x): errors.append(0)

            line = ax.plot(x, y, label=f'{side} {group_labels[i]}', color=palette[i], linestyle=line_styles[j], linewidth=linewidth, zorder=zorder)
            ax.scatter(x, y, color=[scatter_color] * len(x))
            ax.fill_between(x, [y_val - err if y_val is not np.nan else 0 for y_val, err in zip(y, errors)], 
                            [y_val + err if y_val is not np.nan else 0 for y_val, err in zip(y, errors)], 
                            color=palette[i], alpha=0.3)

    plt.xlabel(xlabel, family=font_family, size=font_size)
    sns.despine(left=True, bottom=False)
    ax.set_xticks(range(len(x)))
    ax.set_xticklabels(x, fontsize=font_size)
    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True)) 

    ax.set_ylabel(ylabel, family=font_family, size=font_size)
    ax.yaxis.set_label_coords(*y_label_coords)
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_ticklabels, size=font_size)
    ax.yaxis.grid(True, linestyle='-', which='major', color='lightgrey', alpha=0.5, zorder=-100)
    plt.ylim(y_lim)
    plt.subplots_adjust(left=0.1, right=0.8)

    if legend:
        ax.legend(title=legend_title, 
                  frameon=False,
                  ncol=1, 
                  bbox_to_anchor=bbox_to_anchor,
                  loc=legend_loc,
                  fontsize=font_size,
                  title_fontsize=font_size)

    fig.savefig(f'{directory}/plot.png', format='png')
    plt.show()



@hydra.main(config_path="config", config_name="config")
def combine(args: DictConfig) -> None:
    folder = os.path.join(hydra.utils.get_original_cwd(),args.sim.combine_graph_directory)
    all_list = []
    for directory in os.listdir(folder):
        directory = os.path.join(folder, directory)
        if not os.path.isdir(directory):
            continue
        fixed_list, flex_list = scan_experiment_for_scores(directory=directory)
        all_list.append([fixed_list, flex_list])
    plot_combined_averages(n_runs=5, directory=folder, data = all_list)


if __name__ == '__main__':
    combine()