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

def plot_proposals(user_proposals, assistant_proposals, directory, n_turns):
    x = [i + 1 for i in range(n_turns)]
    plt.plot(x, user_proposals, label="User Proposals", color='red')
    plt.plot(x, assistant_proposals, label="Assistant Proposals", color='blue')
    plt.xlabel('Meta-Prompt Iteration')
    plt.ylabel('Average Amount Proposed')
    graph_title = "Average_Amounts_of_Money_Proposed_to_the_Decider_by_Assistant_and_Users"
    plt.title(" ".join(graph_title.split('_')))
    plt.legend()
    ax = plt.gca()
    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))    
    plt.savefig(f'{directory}_{graph_title}.png', format='png')
    plt.clf()


def plot_average_results(    
    scores,
    data_directory: str = 'sim_res', 
    sim_name: str = 'sim_1',
    sim_id: str = '0',
    ) -> None:
    """
    Plot average user and assistant income when the assistant is a dictator and a decider
    """
    user_scores_dictator, user_scores_decider, assistant_scores_dictator, assistant_scores_decider = [], [], [], []
    user_proposals, assistant_proposals = [], []
    user_scores_dictator = [mean(elem[0]) for elem in scores]
    user_scores_decider = [mean(elem[1]) for elem in scores]
    
    assistant_scores_dictator = [mean(elem[2]) if elem[2] else 0 for elem in scores]
    assistant_scores_decider = [mean(elem[3]) if elem[3] else 0 for elem in scores]
    
    user_proposals = [sum(offer[1] for offer in elem[4]) / len(elem[4]) for elem in scores]
    assistant_proposals = [sum(offer[1] for offer in elem[5]) / len(elem[5]) for elem in scores]
        
    all_scores = [user_scores_dictator, user_scores_decider, assistant_scores_dictator, assistant_scores_decider]
    all_titles = ["Average_User_Dictator_Income_Over_Turns", "Average_User_Decider_Income_Over_Turns", "Average_Assistant_Dictator_Income_Over_Turns", "Average_Assistant_Decider_Income_Over_Turns"]
    for i in range(len(all_scores)):
        plot_scores(all_scores[i], all_titles[i], f"{data_directory}/{sim_name}_id_{sim_id}")
    plot_proposals(user_proposals, assistant_proposals, f"{data_directory}/{sim_name}_id_{sim_id}", len(user_proposals))

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
