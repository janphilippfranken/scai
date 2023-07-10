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
from sentence_transformers import SentenceTransformer, util


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
   
def plot_metrics(
    data: pd.DataFrame,
    metric: str = 'satisfaction',
    error_metric: str = 'rating_id',
    z_column: str = 'agent_id',  
    data_directory: str = 'sim_res/sim_1/0', 
    sim_name: str = 'sim_1',
    sim_id: str = '0',
    run : int = 0,
    palette_name: str = 'colorblind',
    saturation: float = 0.6,
    font_family: str = 'Avenir',
    font_size: int = 24,
    width: int = 10,
    height: int = 5,
    linewidth: int = 2,
    zorder: int = 1,
    scatter_color: str = 'black',
    y_label: str = 'Satisfaction',
    y_label_coords: Tuple[float, float] = (-0.07, 0.5),
    y_ticks: List[int] = [0, 2, 4, 6, 8, 10],
    y_ticklabels: List[int] = [0, 2, 4, 6, 8, 10],
    y_lim: Tuple[float, float] = (-1, 11),
    legend: bool = True,
    legend_title: str = 'User',
    legend_loc: str = 'center left',
    bbox_to_anchor: Tuple[float, float] = (1.0, 0.6),
    plot_error: bool = False,
) -> None:
    """
    Plot user data
    """
    # Get color palette
    palette = get_palette(n=len(set(data[z_column])), palette_name=palette_name, saturation=saturation)
    
    # Set font family and size
    plt.rcParams['font.family'] = font_family
    plt.rcParams['font.size'] = font_size

    # Create figure 
    fig, ax = plt.subplots(figsize=(width, height))

    # Store lines for legend
    lines = []  

    # Plot data
    for i, user in enumerate(set(data[z_column])):
        color = palette[i]
        if not plot_error:
            x = data[data[z_column] == user]['epoch']
            y = data[data[z_column] == user][metric]
            line = ax.plot(x, y, color=color, linewidth=linewidth, zorder=zorder)
            lines.append(line[0])  # Append the Line2D object, not the list
            ax.scatter(x, y, color=[lighten_color(scatter_color)]*len(x)) 
        else:
            x = data[data[z_column] == user]['epoch']
            x = x[:len(x)//2]
            y = np.array(data[(data[z_column] == user) & (data[error_metric] == 'mean')][metric])
            error = np.array(data[(data[z_column] == user) & (data[error_metric] == 'sem')][metric])
            line = ax.plot(x, y, color=color, linewidth=linewidth, zorder=zorder)
            lines.append(line[0])  # Append the Line2D object, not the list
            ax.scatter(x, y, color=[lighten_color(scatter_color)]*len(x)) 
            ax.fill_between(x, y - 1.95 * error, y + 1.95 * error, color=color, alpha=0.3)
    sns.despine(left=True, bottom=False)
    # x-axis
    plt.xlabel('Turns')
    # y-axis
    ax.set_ylabel(y_label.capitalize())
    ax.yaxis.set_label_coords(*y_label_coords)
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_ticklabels)
    ax.yaxis.grid(True, linestyle='-', which='major', color='lightgrey', alpha=0.5, zorder=-100)
    plt.ylim(y_lim)
    # legend 
    if legend:
        ax.legend(lines, 
                  data[z_column].unique(), 
                  title=legend_title, 
                  frameon=False,
                  ncol=1, 
                  bbox_to_anchor=bbox_to_anchor,
                  loc=legend_loc)
    # save plots 
    plt.savefig(f'{data_directory}/{sim_name}_id_{sim_id}_run_{run}_{metric.replace(" ", "_").lower()}.pdf', bbox_inches='tight')
    plt.savefig(f'{data_directory}/{sim_name}_id_{sim_id}_run_{run}_{metric.replace(" ", "_").lower()}.jpg', bbox_inches='tight') # for demo in browser

def plot_average_metrics(
    data: pd.DataFrame,
    data_directory: str = 'sim_res/sim_1/0', 
    sim_name: str = 'sim_1',
    sim_id: str = '0',
    palette_name: str = 'colorblind',
    saturation: float = 0.6,
    font_family: str = 'Avenir',
    font_size: int = 24,
    width: int = 10,
    height: int = 5,
    linewidth: int = 2,
    zorder: int = 1,
    scatter_color: str = 'black',
    y_label: str = 'Average Rating',
    y_label_coords: Tuple[float, float] = (-0.07, 0.5),
    y_ticks: List[int] = [0, 2, 4, 6, 8, 10],
    y_ticklabels: List[int] = [0, 2, 4, 6, 8, 10],
    y_lim: Tuple[float, float] = (-1, 11),
    legend: bool = True,
    legend_title: str = 'Metric',
    legend_loc: str = 'center left',
    bbox_to_anchor: Tuple[float, float] = (1.0, 0.6),
) -> None:
    """
    Plot user data across runs.
    """
    # Get color palette
    palette = get_palette(n=len(set(data['run'])), palette_name=palette_name, saturation=saturation)
    
    # Set font family and size
    plt.rcParams['font.family'] = font_family
    plt.rcParams['font.size'] = font_size

    # Create figure 
    fig, ax = plt.subplots(figsize=(width, height))

    # Store lines for legend
    lines = []  

    # Plot data
    for i, metric in enumerate(set(data['metric'])):
        color = palette[i]
        x = data['run'].unique()
        values = data[data['metric'] == metric]
        y = np.array(values[values['statistic'].str.contains('mean')]['value'])
        error = np.array(values[values['statistic'].str.contains('standard_error')]['value'])
        line = ax.plot(x, y, color=color, linewidth=linewidth, zorder=zorder)
        lines.append(line[0])  # Append the Line2D object, not the list
        ax.scatter(x, y, color=[lighten_color(scatter_color)]*len(x)) 
        ax.fill_between(x, y - 1.95 * error, y + 1.95 * error, color=color, alpha=0.3)


    plt.xlabel('Runs')
    sns.despine(left=True, bottom=False)
    
    # y-axis
    ax.set_ylabel(y_label)
    ax.yaxis.set_label_coords(*y_label_coords)
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_ticklabels)
    ax.yaxis.grid(True, linestyle='-', which='major', color='lightgrey', alpha=0.5, zorder=-100)
    plt.ylim(y_lim)
    # legend 
    if legend:
        ax.legend(lines, 
                  data['metric'].unique(), 
                  title=legend_title, 
                  frameon=False,
                  ncol=1, 
                  bbox_to_anchor=bbox_to_anchor,
                  loc=legend_loc)
    # save plots 
    plt.savefig(f'{data_directory}/{sim_name}_id_{sim_id}_main_res.pdf', bbox_inches='tight')
    plt.savefig(f'{data_directory}/{sim_name}_id_{sim_id}_main_res.jpg', bbox_inches='tight') # for demo in browser

def plot_cosine_similarity(
    data_directory: str = 'sim_res/sim_1/0', 
    sim_name: str = 'sim_1',
    sim_id: str = '0',
    n_runs: int = 5,
    metrics: List[str] = ["Revised Developer Constitution", "Revised Social Contract"],
    palette_name: str = 'colorblind',
    saturation: float = 0.6,
    font_family: str = 'Avenir',
    font_size: int = 24,
    model_name: str = 'all-MiniLM-L6-v2', 
    max_seq_length:  int = 512,
) -> None:
    """
    Plot cosine similarity between system responses over runs.
    """
    # plot params
    plt.rcParams['font.family'] = font_family
    plt.rcParams['font.size'] = font_size
    # get model
    model = SentenceTransformer(model_name)
    model.max_seq_length = max_seq_length
    # load data
    system_messages = {k: [] for k in metrics}
    for run in range(n_runs):
        with open(f'{data_directory}/{sim_name}_id_{sim_id}_run_{run}.json', 'r') as f:
            data = json.load(f)
        for metric in metrics:
            system_messages[metric].append(data['system'][-1]["full_response"][metric])
    # write system messages to json
    with open(f'{data_directory}/{sim_name}_id_{sim_id}_system_messages.json', 'w') as f:
        json.dump(system_messages, f)
    # Get color palette
    palette = sns.color_palette("mako", as_cmap=True)
    # Create a 1x2 subplot grid
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    # First heatmap
    embeddings_0 = model.encode(system_messages[metrics[0]], convert_to_tensor=True)
    cosine_scores_0 = np.triu(util.cos_sim(embeddings_0, embeddings_0), k=0)
    sns.heatmap(cosine_scores_0, linewidths=0.5, cmap=palette, annot=True, ax=axes[0])
    axes[0].set_title(metrics[0].split()[-1])
    axes[0].set_xlabel('Run')
    axes[0].set_ylabel('Run')
    # Second heatmap
    embeddings_1 = model.encode(system_messages[metrics[1]], convert_to_tensor=True)
    cosine_scores_1 = np.triu(util.cos_sim(embeddings_1, embeddings_1), k=0)
    sns.heatmap(cosine_scores_1, linewidths=0.5, cmap=palette, annot=True, ax=axes[1])
    axes[1].set_title(metrics[1].split()[-1])
    axes[1].set_xlabel('Run')
    axes[1].set_ylabel('Run')
    # Adjust the layout and spacing
    plt.tight_layout()
    # Save the figure
    plt.savefig(f'{data_directory}/{sim_name}_id_{sim_id}_cosine_similarity.pdf', bbox_inches='tight')
    plt.savefig(f'{data_directory}/{sim_name}_id_{sim_id}_cosine_similarity.jpg', bbox_inches='tight')