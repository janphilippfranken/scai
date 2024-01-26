from typing import (
    List,
    Tuple,
)
import os
import pandas as pd 
import numpy as np
import json

import colorsys
import seaborn as sns
from matplotlib.axes import Axes
import matplotlib.colors as mc
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import matplotlib.ticker as ticker
from sentence_transformers import SentenceTransformer, util
from scipy.stats import sem

from utils import save_plot_data_as_csv



def change_saturation(
    rgb: Tuple[float, float, float],
    saturation: float = 0.6,
) -> Tuple[float, float, float]:
    """
    Changes the saturation of a color by a given amount. 
    Args:
        rgb (tuple): rgb color
        saturation (float, optional): saturation chante. 
    """
    hsv = colorsys.rgb_to_hsv(rgb[0], rgb[1], rgb[2])
    saturation = max(0, min(hsv[1] * saturation, 1))
    return colorsys.hsv_to_rgb(hsv[0], saturation, hsv[2])

def get_palette(
    n: int = 3,
    palette_name: str = 'colorblind',
    saturation: float = 0.6,
) -> List[Tuple[float, float, float]]:
    """
    Get color palette
    Args:
        n (int, optional): number of colors. 
        palette (str, optional): color palette. Defaults to 'colorblind'.
        saturation (float, optional): saturation of the colors. Defaults to 0.6.
    """
    palette = sns.color_palette(palette_name, n)
    return [change_saturation(color, saturation) for color in palette]

def lighten_color(
    color, 
    amount=0.5, 
    desaturation=0.2,
) -> Tuple[float, float, float]:
    """
    Copy-pasted from Eric's slack.
    Lightens and desaturates the given color by multiplying (1-luminosity) by the given amount
    and decreasing the saturation by the specified desaturation amount.
    Input can be matplotlib color string, hex string, or RGB tuple.
    Examples:
    >> lighten_color('g', 0.3, 0.2)
    >> lighten_color('#F034A3', 0.6, 0.4)
    >> lighten_color((.3,.55,.1), 0.5, 0.1)
    """
    try:
        c = mc.cnames[color]
    except KeyError:
        c = color
    h, l, s = colorsys.rgb_to_hls(*mc.to_rgb(c))
    return colorsys.hls_to_rgb(h, 1 - amount * (1 - l), max(0, s - desaturation))

def get_fancy_bbox(
    bb, 
    boxstyle, 
    color, 
    background=False, 
    mutation_aspect=3,
) -> FancyBboxPatch:
    """
    Copy-pasted from Eric's slack.
    Creates a fancy bounding box for the bar plots.
    """
    if background:
        height = bb.height - 2
    else:
        height = bb.height
    if background:
        base = bb.ymin # - 0.2
    else:
        base = bb.ymin
    return FancyBboxPatch(
        (bb.xmin, base),
        abs(bb.width), height,
        boxstyle=boxstyle,
        ec="none", fc=color,
        mutation_aspect=mutation_aspect, # change depending on ylim
        zorder=2)

def plot_all_averages(
                   total_scores: list,
                   all_score_lsts: list,
                   currencies: List,
                   questions: dict,
                   n_runs: int, 
                   directory: str,
                   edge_case: bool,
                   sim_dir: str,
                   sim_id: str,
                   linewidth: int = 2,
                   zorder: int = 1,
                   scatter_color: str = 'black',
                   ):
    data_list = [[] for _ in range(4)]
    for elem in total_scores:
        for i in range(4):
            data_list[i].append(elem[i][0])

    income_list = [[] for _ in range(4)]
    for elem in all_score_lsts:
        for i in range(4):
            income_list[i].append(elem[i])


    save_plot_data_as_csv(f'{directory}/all_plot_data', n_runs, data_list, ["Fixed Plot Data",
                                                                       "Flexible Plot Data",
                                                                       "Fixed Bar Data",
                                                                       "Flexible Bar Data",
                                                                       ])
    save_plot_data_as_csv(f'{directory}/all_plot_data', n_runs, income_list, ["Fixed Dictator Income Data",
                                                                       "Fixed Decider Income Data",
                                                                       "Flexible Dictator Income Data",
                                                                       "Flexible Decider Income Data"])

    all_score_lsts = np.array(all_score_lsts)
    all_score_lsts = all_score_lsts.transpose(1, 2, 0)

    total_scores = np.array(total_scores)

    mean_matrix = np.nanmean(total_scores, axis=0)
    mean_matrix = mean_matrix.reshape(1, total_scores.shape[1], total_scores.shape[2], total_scores.shape[3])
    sem_matrix = sem(total_scores, nan_policy='omit', axis=0)
    sem_matrix = sem_matrix.reshape(1, total_scores.shape[1], total_scores.shape[2], total_scores.shape[3])
    flattened_scores = np.concatenate([mean_matrix, sem_matrix], axis=0)

    list_fixed_plots = flattened_scores[:, 0, :, :]
    list_flex_plots = flattened_scores[:, 1, :, :]
    list_fixed_bars = flattened_scores[:, 2, :, :]
    list_flex_bars = flattened_scores[:, 3, :, :]

    # Plot Plots
    lines = []
    
    palette = sns.color_palette("mako", 2)

    x = [f"Iteration: {i+1}" for i in range(n_runs)]


    for j in range(len(currencies)):
        if not edge_case:
            _, ax = plt.subplots(figsize=(20, 10))
            for i, item in enumerate([list_fixed_plots, list_flex_plots]):
                label = "Fixed Agent" if not i else "Flexible Agent"
                #y = [z[j] for z in item[0] if z[j] is not np.nan]
                y = item[0][j]

                errors = item[1][j]

                while len(y) < len(x): y.append(np.nan)
                while len(errors) < len(x): errors.append(0)

                line = ax.plot(x, y, color=palette[i], linewidth=linewidth, zorder=zorder, label=label)
                lines.append(line[0])
                ax.scatter(x, y, color=[lighten_color(scatter_color)] * len(x)) 
                ax.fill_between(x, [y_val - 1.95 * err if y_val is not np.nan else 0 for y_val, err in zip(y, errors)], [y_val + 1.95 * err if y_val is not np.nan else 0 for y_val, err in zip(y, errors)], color=palette[i], alpha=0.3)

            plot_proposal_line_graph(ax=ax,
                                    x=x,
                                    graph_title=f"Average_Proportion_of_{currencies[j]}_Offered_to_the_Decider_Across_all_Iterations",
                                    xlabel='Meta-Prompt Iteration',
                                    ylabel='Average Proportion of Total Proposed',
                                    directory=f'{directory}/'
                                    )
        else:

            # Extract y values for each agent type for the current currency
            y_fixed_current = list_fixed_plots[0][j]
            y_flexible_current = list_flex_plots[0][j]

            y_fixed_errors = list_fixed_plots[1][j]
            y_flexible_errors = list_flex_plots[1][j]
            plot_bar_graph(directory=directory,
                           sim_dir=sim_dir,
                           sim_id="fixed_agent",
                           graph_title=f"Average_Proportion_of_{currencies[j]}_Offered_to_the_Decider_Across_all_Iterations",
                           xlabel='Fixed Agent',
                           ylabel='Average Proportion of Total Proposed',
                           path_suffix="bar",
                           x=[""],
                           y=y_fixed_current,
                           errors=y_fixed_errors)

            plot_bar_graph(directory=directory,
                           sim_dir=sim_dir,
                           sim_id="flexible_agent",
                           graph_title=f"Average_Proportion_of_{currencies[j]}_Offered_to_the_Decider_Across_all_Iterations",
                           xlabel='Flexible Agent',
                           ylabel='Average Proportion of Total Proposed',
                           path_suffix="bar",
                           x=[""],
                           y=y_flexible_current,
                           errors=y_flexible_errors)
            
        plt.clf()

    # Fixed Bars
    y = list_fixed_bars[0][0]
    errors = list_fixed_bars[1][0]
    plot_bar_graph(directory=directory, 
                   sim_dir=sim_dir,
                   sim_id=sim_id,
                   graph_title="Percentage of Proposal Acceptance for Fixed-Policy Agents",
                   ylabel='Percentage of Proposals Accepted',
                   xlabel = 'Meta-Prompt-Iteration',
                   path_suffix="fix_bar",
                   x=x,
                   y=y,
                   errors=errors)
    #Flex Bars
    y = list_flex_bars[0][0]
    errors = list_flex_bars[1][0]
    plot_bar_graph(directory=directory, 
                   sim_id=sim_id,
                   sim_dir=sim_dir,
                   graph_title="Percentage of Proposal Acceptance for Flexible-Policy Agents",
                   ylabel='Percentage of Proposals Accepted',
                   xlabel = 'Meta-Prompt-Iteration',
                   path_suffix="flex_bar",
                   x=x,
                   y=y,
                   errors=errors)

    all_means = []
    all_errors = []
    for inner_list in all_score_lsts:
        means = np.mean(inner_list, axis=1)
        errors = sem(inner_list, axis=1)
        all_means.append(means)
        all_errors.append(errors)

    plot_scores(all_means, f'{directory}/', all_errors)
    plot_currencies_and_questions(questions, f'{directory}/')
    
def plot_currencies_and_questions(questions, directory):
    for currency, values in questions.items():
        plot_bar_graph(directory, "", currency, f"Question_Asked_When_Splitting_{currency}", "Proportion of Interactions Where Question was Asked", f"{currency}", "", [""], [sum(values) / len(values)], sem(values), font_size=18)


def plot_proposal_line_graph(ax: Axes,
                             x: list,
                             graph_title: str,
                             xlabel: str,
                             ylabel: str,
                             directory: str,
                             font_family: str = 'Avenir',
                             font_size: int = 24,
                             y_label_coords: Tuple[float, float] = (-0.07, 0.5),
                             y_ticks: List[int] = [0, 0.2, 0.4, 0.6, 0.8, 1],
                             y_ticklabels: List[int] = [0, 20, 40, 60, 80, 100],
                             y_lim: Tuple[float, float] = (-0.1, 1.1),
                             legend: bool = True,
                             legend_title: str = 'Agent',
                             legend_loc: str = 'center left',
                             bbox_to_anchor: Tuple[float, float] = (1.0, 0.6),
                             ):

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

    #graph_title = f"Average_Proportion_of_Currency_Offered_to_the_Decider_Across_all_Iterations"
    plt.title(" ".join(graph_title.split('_')), family=font_family, size=font_size + 5)
    if legend:
        ax.legend(title=legend_title, 
                  frameon=False,
                  ncol=1, 
                  bbox_to_anchor=bbox_to_anchor,
                  loc=legend_loc,
                  fontsize=font_size,  # Change the font size of legend items
                  title_fontsize=font_size
                  )

    plt.savefig(f'{directory}_{graph_title}.png', format='png')
    plt.clf()


def plot_bar_graph(directory: str,
                   sim_dir: str,
                   sim_id: str,
                   graph_title: str,
                   ylabel: str,
                   xlabel: str,
                   path_suffix: str,
                   x: list,
                   y: list,
                   errors: list,
                   font_family = 'Avenir',
                   font_size = 24
                   ):
    plt.rcParams['font.family'] = font_family
    plt.rcParams['font.size'] = font_size
    plt.bar(x, y, yerr=errors)
    plt.xlabel(xlabel, fontsize=font_size)

    plt.ylabel(ylabel, fontsize=font_size)
    graph_title = " ".join(graph_title.split('_'))
    plt.title(graph_title, fontsize=font_size)

    for i in range(len(y)):
        if np.isnan(y[i]):
            plt.text(i, 0, 'No data\nprovided', ha='center', va='bottom')

    ax = plt.gca()
    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    # Specify the full file path where you want to save the figure
    directory_path = f'{directory}/id_{sim_id}__{graph_title}_{path_suffix}.png'
    os.makedirs(os.path.dirname(directory_path), exist_ok=True)
    plt.savefig(directory_path, format='png')
    plt.clf()

def plot_proposals(list_fixed: list,
                   list_flex: int,
                   currency: str, 
                   amounts_per_run: list,
                   n_runs: int, 
                   directory: str,
                   linewidth: int = 2,
                   zorder: int = 1,
                   scatter_color: str = 'black'):
    # Set font family and size

    _, ax = plt.subplots(figsize=(20, 10))
    lines = []
 
    palette = sns.color_palette("mako", 2)

    x = [f"{i + 1}: {amounts_per_run[i]} {currency}" for i in range(n_runs)]

    for i, item in enumerate([list_fixed, list_flex]):
        label = "Fixed Agent" if not i else "Flexible Agent"
        item = [z for z in item if z is not np.nan]

        y = [float(sum(item[k])) / (amounts_per_run[k] * len(item[k])) for k in range(len(item))]

        while len(y) < len(x):
            y.append(np.nan)

        errors = []
        
        for j, elem in enumerate(item):
            elem = [float(elem[h]) / amounts_per_run[j] for h in range(len(elem)) if elem[h] is not np.nan]
            errors.append(sem(elem))

        while len(errors) < len(x):
            errors.append(0)

        line = ax.plot(x, y, color=palette[i], linewidth=linewidth, zorder=zorder, label=label)
        lines.append(line[0])
        ax.scatter(x, y, color=[lighten_color(scatter_color)] * len(x)) 
        ax.fill_between(x, [y_val - 1.95 * err if y_val is not np.nan else 0 for y_val, err in zip(y, errors)], [y_val + 1.95 * err if y_val is not np.nan else 0 for y_val, err in zip(y, errors)], color=palette[i], alpha=0.3)
        if not i:
            y_fixed = y
        else:
            y_flex = y

    plot_proposal_line_graph(ax=ax,
                            x=x,
                            graph_title=f"Proportion_of_{currency}_Offered_to_the_Decider_Across_all_Iterations",
                            xlabel='Meta-Prompt Iteration',
                            ylabel='Proportion of Total Proposed',
                            directory=directory
                            )
    plt.clf()
    
    return y_fixed, y_flex

# Collect the proposals
def collect_proposals(scores: list, 
                      currencies: list, 
                      agent_index: int):
    agent_proposals = []
    for score in scores:
        for currency in currencies:
            dict_offer = [amount_dict[currency][1] for amount_dict in score[agent_index] if currency in amount_dict]
            agent_proposals.append({currency: dict_offer if dict_offer else np.nan})
    return agent_proposals

def plot_results(    
    scores: list,
    currencies: list,
    amounts_per_run: list,
    n_runs: int,
    data_directory: str = 'sim_res', 
    sim_name: str = 'sim_1',
    sim_id: str = '0',
    ):
    """
    Plot average user and assistant income when the assistant is a dictator and a decider
    """
    # user_scores_dictator, user_scores_decider, assistant_scores_dictator, assistant_scores_decider, user_proposals, assistant_proposals
    fixed_dict_scores, fixed_deci_scores, flex_dict_scores, flex_deci_scores = [], [], [], []
    all_score_lsts = [fixed_dict_scores, fixed_deci_scores, flex_dict_scores, flex_deci_scores]
    num_score_lists = 4
    for i in range(len(scores)):
        for j in range(num_score_lists):
            total, earned = 0, 0
            for value in scores[i][j]:
                if value != -1:
                    total += amounts_per_run[i]
                    if value:
                        for currency in currencies:
                            earned += value[currency]
            if total:
                all_score_lsts[j].append(float(earned / total))
            else:
                all_score_lsts[j].append(-1)
    
    plot_scores(all_score_lsts, f"{data_directory}/id_{sim_id}_", None)

    # Plot proposals:
    fixed_agent_proposals, flexible_agent_proposals = [], []
    fixed_agent_index, flexible_agent_index = 4, 5
    # Get the proposals offered by the fixed and flex agents
    fixed_agent_proposals = collect_proposals(scores, currencies, fixed_agent_index)
    flexible_agent_proposals = collect_proposals(scores, currencies, flexible_agent_index)
    # Get the relevant statistics and plot the proposals

    all_currency_plots = []
    for currency in currencies:
        list_fixed_proportions = [elem[currency] for elem in fixed_agent_proposals if currency in elem]
        list_flex_proportions = [elem[currency] for elem in flexible_agent_proposals if currency in elem]
        y_fixed_plot, y_flex_plot = plot_proposals(list_fixed_proportions, list_flex_proportions, currency, amounts_per_run, n_runs, f"{data_directory}/id_{sim_id}")
        all_currency_plots.append([y_fixed_plot, y_flex_plot])
    all_currency_plots = np.array(all_currency_plots)
    all_currency_plots.transpose(1, 0, 2)

    # Plot Acceptance/Rejection Tables:
    fixed_dictator_scores, fixed_decider_scores, flex_dictator_scores, flex_decider_scores = [], [], [], []
    for score in scores:
        fixed_dictator_scores.append(score[0])
        fixed_decider_scores.append(score[1])
        flex_dictator_scores.append(score[2])
        flex_decider_scores.append(score[3])

    titles = ["Rate_of_Fixed-Policy_Agent_Acceptance_per_Iteration", "Rate_of_Flexible-Policy_Agent_Acceptance_per_Iteration"]
    for i, score_list in enumerate([(fixed_dictator_scores, fixed_decider_scores), (flex_dictator_scores, flex_decider_scores)]):
        if not i:
            y_fixed_bar = plot_rates(score_list[1], f"{data_directory}/id_{sim_id}", titles[i], n_runs)
        else:
            y_flex_bar = plot_rates(score_list[1], f"{data_directory}/id_{sim_id}", titles[i], n_runs)
        
    y_fixed_plot = all_currency_plots[:, 0, :]
    y_flex_plot = all_currency_plots[:, 1, :]
        
    return y_fixed_plot.tolist(), y_flex_plot.tolist(), [y_fixed_bar]*len(currencies), [y_flex_bar]*len(currencies), all_score_lsts

def plot_scores(all_scores, path, errors):
    labels = ['Fixed Agent', 'Flexible Agent']
    titles = ['Average_Income_Earned_by_Dictators_Over_Iterations', 'Average_Income_Earned_by_Deciders_Over_Iterations']
    for i in range(2):
        list1 = all_scores[i]
        list2 = all_scores[i + 2]

        # Define the x locations for the groups
        x = np.arange(len(list1))

        # Set the width of the bars
        width = 0.35

        # Plot the bars
        fig, ax = plt.subplots()
        if errors:
            rects1 = ax.bar(x - width/2, list1, width, label=labels[0], yerr=errors[i])
            rects2 = ax.bar(x + width/2, list2, width, label=labels[1], yerr=errors[i + 2])
        else:
            rects1 = ax.bar(x - width/2, list1, width, label=labels[0])
            rects2 = ax.bar(x + width/2, list2, width, label=labels[1])

        # Add labels, title, and legend
        ax.set_ylabel('Proportion of Income Earned', fontsize=12)
        ax.set_title(' '.join(titles[i].split('_')), fontsize=14)
        ax.set_xticks(x)
        ax.tick_params(axis='y', labelsize=10)
        ax.set_xlabel('Meta-Prompt-Iteration', fontsize=12)
        ax.set_xticklabels([f"Iteration {i + 1}" for i in range(len(list1))], fontsize=10)  # You can set your custom labels
        ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        ax.legend(fontsize=10)

        plt.savefig(f'{path}{titles[i]}.png', format='png')
        plt.clf()
    
def plot_rates(scores: list, 
                path: str, 
                title: str, 
                n_runs: int,
                font_family: str = 'Avenir', 
                font_size: int = 24):
    acceptance_rates = []
    for score in scores:
        total, total_accepted = 0, 0
        for dict in score:
            if dict != -1:
                total += 1
                if dict != 0:
                    total_accepted += 1
        if total:
            acceptance_rates.append(float(total_accepted) / float(total))
        else: 
            acceptance_rates.append(np.nan)

    plt.rcParams['font.family'] = font_family
    plt.rcParams['font.size'] = font_size

    x = [f"{i + 1}" for i in range(n_runs)]
    plt.bar(x, acceptance_rates)
    plt.xlabel('Meta-Prompt-Iteration')

    plt.ylabel(f'Percentage of Proposals Accepted')
    graph_title = " ".join(title.split('_'))
    plt.title(graph_title)

    for i in range(len(acceptance_rates)):
        if np.isnan(acceptance_rates[i]):
            plt.text(i, 0, 'No data\nprovided', ha='center', va='bottom')

    ax = plt.gca()
    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    # Specify the full file path where you want to save the figure
    plt.savefig(f'{path}_{title}.png', format='png')
    plt.clf()
    return acceptance_rates

def plot_questions(ood: list,
                   in_d: list,
                   directory: str,
                   ):
    if len(ood) > 0:
        errors_ood = sem(ood)
        plot_bar_graph(directory, "0", "0", "Questions_asked_when_posed_with_an OOD_currency", "Percentage of Questions Asked", "Flexible Agent", "", [""], [sum(ood) / len(ood)], errors_ood)
    if len(in_d) > 0:
        errors_in_d = sem(in_d)
        plot_bar_graph(directory, "0", "0", "Questions_asked_when_posed_with_an_Ind_currency", "Percentage of Questions Asked", "Flexible Agent", "", [""], [sum(in_d) / len(in_d)], errors_in_d)


def plot_cosine_similarity(
    system_messages,
    social_contract,
    data_directory: str = 'sim_res/sim_1/0', 
    sim_name: str = 'sim_1',
    sim_id: str = '0',
    font_family: str = 'Avenir',
    font_size: int = 12,
    model_name: str = 'all-MiniLM-L6-v2', 
    max_seq_length:  int = 512,
) -> None:
    """
    Plot cosine similarity between system responses over runs.
    """
    social_contracts = [social_contract for i in range(len(system_messages))]
    # plot params
    plt.clf()
    plt.rcParams['font.family'] = font_family
    plt.rcParams['font.size'] = font_size
    # get model
    model = SentenceTransformer(model_name)
    model.max_seq_length = max_seq_length
    # write system messages to json
    with open(f'{data_directory}/id_{sim_id}_system_messages.json', 'w') as f:
        json.dump(system_messages, f)
    # Make heatmap
    embeddings_0 = model.encode(system_messages, convert_to_tensor=True)
    embeddings_1 = model.encode(social_contracts, convert_to_tensor=True)
    cosine_scores_0 = np.triu(util.cos_sim(embeddings_0, embeddings_1), k=0)
    last_column = cosine_scores_0[:, -1]
    plt.plot(range(len(last_column)), last_column)
    plt.title('Semantic Entropy Across Meta-prompt Epochs')
    plt.xlabel('Run')
    plt.ylabel('Cosine Similarity')
    ax = plt.gca()  # gca stands for 'get current axis'
    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))    
    plt.savefig(f'{data_directory}/id_{sim_id}_cosine_similarity.pdf', bbox_inches='tight')
    plt.savefig(f'{data_directory}/id_{sim_id}_cosine_similarity.jpg', bbox_inches='tight')
