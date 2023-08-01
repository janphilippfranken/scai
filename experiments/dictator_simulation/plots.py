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

def plot_scores(scores, title, path):
    x_labels = list(range(1, len(scores) + 1))
    plt.bar(x_labels, scores)
    plt.xlabel('Iteration')
    plt.ylabel(f'Average income per interaction')
    graph_title = " ".join(title.split('_'))
    plt.title(graph_title)
    ax = plt.gca()
    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    # Specify the full file path where you want to save the figure
    plt.savefig(f'{path}_{title}.png', format='png')
    plt.clf()

def plot_proposals(list_fixed_proportions: list, 
                   list_flex_proportions: list, 
                   currency: str, 
                   amounts_per_run: int,
                   n_runs: int, 
                   directory: str,
                   font_family: str = 'Avenir',
                   font_size: int = 24,
                   palette_name: str = 'colorblind',
                   saturation: float = 0.6,
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
    x = [f"{i + 1}: {amounts_per_run[i]} {currency}" for i in range(n_runs)]
    # Set font family and size

    fig, ax = plt.subplots(figsize=(20, 10))

    plt.rcParams['font.family'] = font_family
    plt.rcParams['font.size'] = font_size

    lines = []

    palette = sns.color_palette("husl", 2)

    list_fixed_proportions = [x for x in list_fixed_proportions if x is not None]
    list_flex_proportions = [x for x in list_flex_proportions if x is not None]
    for i, elem in enumerate([list_flex_proportions, list_fixed_proportions]):
        if not elem:
            continue
        
        standard_error = np.std(elem, ddof=1) / math.sqrt(len(elem))

        line = ax.plot(x, elem, color=palette[i], linewidth=linewidth, zorder=zorder)

        lines.append(line[0])

        ax.scatter(x, elem, color=[lighten_color(scatter_color)]*len(x))

        ax.fill_between(x, elem - 1.95 * standard_error, elem + 1.95 * standard_error, color=palette[i], alpha=0.3)

    plt.xlabel('Meta-Prompt Iteration')
    sns.despine(left=True, bottom=False)

    ax.set_ylabel('Average Proportion of Total Proposed')
    ax.yaxis.set_label_coords(*y_label_coords)
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_ticklabels)
    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True)) 
    ax.yaxis.grid(True, linestyle='-', which='major', color='lightgrey', alpha=0.5, zorder=-100)
    plt.ylim(y_lim)

    graph_title = f"Proportions_of_{currency}_Proposed_by_Assistant_and_Users"
    plt.title(" ".join(graph_title.split('_')))
    if legend:
        ax.legend(lines,
                    ["Flexible Agent", "Fixed Agent"],
                    title=legend_title, 
                    frameon=False,
                    ncol=1, 
                    bbox_to_anchor=bbox_to_anchor,
                    loc=legend_loc) 
    plt.savefig(f'{directory}_{graph_title}.png', format='png')
    plt.clf()

def plot_average_results(    
    scores,
    currencies,
    amounts_per_run,
    n_runs,
    data_directory: str = 'sim_res', 
    sim_name: str = 'sim_1',
    sim_id: str = '0',
    ) -> None:
    """
    Plot average user and assistant income when the assistant is a dictator and a decider
    """
    # user_scores_dictator, user_scores_decider, assistant_scores_dictator, assistant_scores_decider = [], [], [], []
    # user_scores_dictator = [mean(elem[0]) for elem in scores]
    # user_scores_decider = [mean(elem[1]) for elem in scores]
    
    # assistant_scores_dictator = [mean(elem[2]) if elem[2] else 0 for elem in scores]
    # assistant_scores_decider = [mean(elem[3]) if elem[3] else 0 for elem in scores]
    fixed_agent_proposals, flexible_agent_proposals = [], []
    for i in range(len(scores)):
        for currency in currencies:
            fixed_dict_offer = 0
            len_dict = 0
            for amount_dict in scores[i][4]:
                if currency in amount_dict:
                    fixed_dict_offer += amount_dict[currency][1]
                    len_dict += 1

            if len_dict == 0:
                fixed_agent_proposals.append({currency: None})
            else:
                fixed_agent_proposals.append({currency: float(fixed_dict_offer) / float(amounts_per_run[i] * len_dict)})
            
        
            flex_dict_offer = 0
            len_deci = 0
            for amount_dict in scores[i][5]:
                if currency in amount_dict:
                    flex_dict_offer += amount_dict[currency][1]
                    len_deci += 1
            if len_deci == 0:
                flexible_agent_proposals.append({currency: None})
            else:
                flexible_agent_proposals.append({currency: float(flex_dict_offer) / float(amounts_per_run[i] * len_deci)})

        
    # all_scores = [user_scores_dictator, user_scores_decider, assistant_scores_dictator, assistant_scores_decider]
    # all_titles = ["Average_User_Dictator_Income_Over_Turns", "Average_User_Decider_Income_Over_Turns", "Average_Assistant_Dictator_Income_Over_Turns", "Average_Assistant_Decider_Income_Over_Turns"]
    # for i in range(len(all_scores)):
    #     plot_scores(all_scores[i], all_titles[i], f"{data_directory}/{sim_name}_id_{sim_id}")
    for currency in currencies:
        list_fixed_proportions = [elem[currency] for elem in fixed_agent_proposals if currency in elem]
        list_flex_proportions = [elem[currency] for elem in flexible_agent_proposals if currency in elem]
        plot_proposals(list_fixed_proportions, list_flex_proportions, currency, amounts_per_run, n_runs, f"{data_directory}/{sim_name}_id_{sim_id}")

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
