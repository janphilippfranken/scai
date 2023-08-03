from typing import (
    List,
    Tuple,
)

import pandas as pd 
import numpy as np
import json

import colorsys
import seaborn as sns
import matplotlib.colors as mc
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import matplotlib.ticker as ticker
from sentence_transformers import SentenceTransformer, util
import math
from scipy.stats import sem
from statistics import mean


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
                   total_scores: List[List[List(float)]],
                   n_runs: int, 
                   directory: str,
                   font_family: str = 'Avenir',
                   font_size: int = 24,
                   linewidth: int = 2,
                   zorder: int = 1,
                   scatter_color: str = 'black',
                   y_label_coords: Tuple[float, float] = (-0.07, 0.5),
                   y_ticks: List[int] = [0, 0.2, 0.4, 0.6, 0.8, 1],
                   y_ticklabels: List[int] = [0, 20, 40, 60, 80, 100],
                   y_lim: Tuple[float, float] = (-0.1, 1.1),
                   legend: bool = True,
                   legend_title: str = 'Agent',
                   legend_loc: str = 'center left',
                   bbox_to_anchor: Tuple[float, float] = (1.0, 0.6),
                   bar_title: str = 'Average Score',
                   ):
    
    # unzip the list of lists of lists
    total_scores = np.array(total_scores)
    mean_matrix = np.nanmean(total_scores, axis=0)
    sem_matrix = sem(total_scores, nan_policy='omit', axis=0)
    flattened_scores = np.concatenate([mean_matrix, sem_matrix], axis=0)

    list_fixed_plots = flattened_scores[:, 0, :]
    list_flex_plots = flattened_scores[:, 1, :]
    list_fixed_bars = flattened_scores[:, 2, :]
    list_flex_bars = flattened_scores[:, 3, :]

    # Plot Plots
    lines = []
    _, ax = plt.subplots(figsize=(20, 10))
    palette = sns.color_palette("mako", 2)

    x = [f"{i+1}" for i in range(n_runs)]

    for i, item in enumerate([list_fixed_plots, list_flex_plots]):
        label = "Fixed Agent" if not i else "Flexible Agent"
        y = [z for z in item[0] if z is not None]

        if not y: continue
        while len(y) < len(x):
            y.append(None)

        errors = item[1]

        while len(errors) < len(x):
            errors.append(0)

        line = ax.plot(x, y, color=palette[i], linewidth=linewidth, zorder=zorder, label=label)
        lines.append(line[0])
        ax.scatter(x, y, color=[lighten_color(scatter_color)] * len(x)) 
        ax.fill_between(x, [y_val - 1.95 * err if y_val is not None else 0 for y_val, err in zip(y, errors)], [y_val + 1.95 * err if y_val is not None else 0 for y_val, err in zip(y, errors)], color=palette[i], alpha=0.3)
        if not i:
            y_fixed = y
        else:
            y_flex = y
            
    plt.xlabel('Meta-Prompt Iteration: Amount and Currency', family=font_family, size=font_size)
    sns.despine(left=True, bottom=False)
    ax.set_xticks(range(len(x)))
    ax.set_xticklabels(x, fontsize=font_size)
    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True)) 

    ax.set_ylabel('Average Proportion of Total Proposed', family=font_family, size=font_size)
    ax.yaxis.set_label_coords(*y_label_coords)
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_ticklabels, size=font_size)
    ax.yaxis.grid(True, linestyle='-', which='major', color='lightgrey', alpha=0.5, zorder=-100)
    plt.ylim(y_lim)
    plt.subplots_adjust(left=0.1, right=0.8)

    graph_title = f"Proportions_Proposed_by_Flexible-Contract_and_Fixed-Contract Agents"
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

    #Graph Bars:
    acceptance_rates = list_fixed_bars[0]
    x = [f"{i + 1}" for i in range(n_runs)]
    plt.bar(x, acceptance_rates)
    plt.xlabel('Meta-Prompt-Iteration')

    plt.ylabel(f'Percentage of Proposals Accepted')
    graph_title = " ".join(bar_title.split('_'))
    plt.title(graph_title)

    for i in range(len(acceptance_rates)):
        if np.isnan(acceptance_rates[i]):
            plt.text(i, 0, 'No data\nprovided', ha='center', va='bottom')

    ax = plt.gca()
    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    # Specify the full file path where you want to save the figure
    plt.savefig(f'{directory}_{graph_title}.png', format='png')
    plt.clf()
    
    return y_fixed, y_flex



def plot_proposals(list_fixed: list,
                   list_flex: int,
                   currency: str, 
                   amounts_per_run: list,
                   n_runs: int, 
                   directory: str,
                   font_family: str = 'Avenir',
                   font_size: int = 24,
                   linewidth: int = 2,
                   zorder: int = 1,
                   scatter_color: str = 'black',
                   y_label_coords: Tuple[float, float] = (-0.07, 0.5),
                   y_ticks: List[int] = [0, 0.2, 0.4, 0.6, 0.8, 1],
                   y_ticklabels: List[int] = [0, 20, 40, 60, 80, 100],
                   y_lim: Tuple[float, float] = (-0.1, 1.1),
                   legend: bool = True,
                   legend_title: str = 'Agent',
                   legend_loc: str = 'center left',
                   bbox_to_anchor: Tuple[float, float] = (1.0, 0.6)):
    # Set font family and size

    _, ax = plt.subplots(figsize=(20, 10))
    lines = []
 
    palette = sns.color_palette("mako", 2)

    x = [f"{i + 1}: {amounts_per_run[i]} {currency}" for i in range(n_runs)]

    for i, item in enumerate([list_fixed, list_flex]):
        label = "Fixed Agent" if not i else "Flexible Agent"
        item = [z for z in item if z is not None]

        y = [float(sum(item[k])) / (amounts_per_run[k] * len(item[k])) for k in range(len(item))]

        if not y:
            continue

        while len(y) < len(x):
            y.append(None)

        errors = []
        
        for j, elem in enumerate(item):
            elem = [float(elem[h]) / amounts_per_run[j] for h in range(len(elem)) if elem[h] is not None]
            errors.append(sem(elem))

        while len(errors) < len(x):
            errors.append(0)

        line = ax.plot(x, y, color=palette[i], linewidth=linewidth, zorder=zorder, label=label)
        lines.append(line[0])
        ax.scatter(x, y, color=[lighten_color(scatter_color)] * len(x)) 
        ax.fill_between(x, [y_val - 1.95 * err if y_val is not None else 0 for y_val, err in zip(y, errors)], [y_val + 1.95 * err if y_val is not None else 0 for y_val, err in zip(y, errors)], color=palette[i], alpha=0.3)
        if not i:
            y_fixed = y
        else:
            y_flex = y


    plt.xlabel('Meta-Prompt Iteration: Amount and Currency', family=font_family, size=font_size)
    sns.despine(left=True, bottom=False)
    ax.set_xticks(range(len(x)))
    ax.set_xticklabels(x, fontsize=font_size)
    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True)) 

    ax.set_ylabel('Average Proportion of Total Proposed', family=font_family, size=font_size)
    ax.yaxis.set_label_coords(*y_label_coords)
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_ticklabels, size=font_size)
    ax.yaxis.grid(True, linestyle='-', which='major', color='lightgrey', alpha=0.5, zorder=-100)
    plt.ylim(y_lim)
    plt.subplots_adjust(left=0.1, right=0.8)

    graph_title = f"Proportions_of_{currency}_Proposed_by_Flexible-Contract_and_Fixed-Contract Agents"
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
    return y_fixed, y_flex


# Collect the proposals
def collect_proposals(scores: list, 
                      currencies: list, 
                      agent_index: int):
    agent_proposals = []
    for score in scores:
        for currency in currencies:
            dict_offer = [amount_dict[currency][1] for amount_dict in score[agent_index] if currency in amount_dict]
            agent_proposals.append({currency: dict_offer if dict_offer else None})
    return agent_proposals

def plot_results(    
    scores: list,
    currencies: list,
    amounts_per_run: list,
    n_runs: int,
    data_directory: str = 'sim_res', 
    sim_name: str = 'sim_1',
    sim_id: str = '0',
    ) -> None:
    """
    Plot average user and assistant income when the assistant is a dictator and a decider
    """
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
        y_fixed_plot, y_flex_plot = plot_proposals(list_fixed_proportions, list_flex_proportions, currency, amounts_per_run, n_runs, f"{data_directory}/{sim_name}_id_{sim_id}")
        all_currency_plots.append([y_fixed_plot, y_flex_plot])
    
    all_currency_plots = np.array(all_currency_plots)
    all_currency_plots.transpose()

    # Plot Acceptance/Rejection Tables:
    fixed_dictator_scores, fixed_decider_scores, flex_dictator_scores, flex_decider_scores = [], [], [], []
    for score in scores:
        fixed_dictator_scores.append(score[0])
        fixed_decider_scores.append(score[1])
        flex_dictator_scores.append(score[2])
        flex_decider_scores.append(score[3])
    titles = ["Rate_of_Fixed-Policy_Agent_Acceptance_per_Iteration", "Rate_of_Flexible-Policy_Agent_Acceptance_per_Iteration"]
    for i, score_list in enumerate([(fixed_dictator_scores, fixed_decider_scores), (flex_dictator_scores, flex_decider_scores)]):
        y_fixed_bar, y_flex_bar = plot_scores(score_list[1], f"{data_directory}/{sim_name}_id_{sim_id}", titles[i], n_runs)
    
    if len(all_currency_plots[0]) <= 1:
        ret_y_fixed_plot = all_currency_plots[0][0]
    if len(all_currency_plots[1]) <= 1:
        ret_y_fixed_plot = all_currency_plots[1][0]

    return ret_y_fixed_plot, ret_y_fixed_plot, y_fixed_bar, y_flex_bar

# def print_scores(scores):

    
def plot_scores(scores: list, 
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
    return 

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
    with open(f'{data_directory}/{sim_name}_id_{sim_id}_system_messages.json', 'w') as f:
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
    plt.savefig(f'{data_directory}/{sim_name}_id_{sim_id}_cosine_similarity.pdf', bbox_inches='tight')
    plt.savefig(f'{data_directory}/{sim_name}_id_{sim_id}_cosine_similarity.jpg', bbox_inches='tight')
