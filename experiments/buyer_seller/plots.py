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
   
from plots import get_palette, lighten_color, get_fancy_bbox
import pandas as pd 
import matplotlib.pyplot as plt
import seaborn as sns

def plot_metrics(
    data: dict,
    data_directory: str = 'sim_res', 
    sim_name: str = 'sim_1',
    sim_id: str = '0',
    run : int = 0,
    palette_name: str = 'colorblind',
    n_colors: int = 2,
    saturation: float = 0.6,
    font_family: str = 'Avenir',
    font_size: int = 24,
    width: int = 15,
    height: int = 5,
) -> None:
    """
    Plot user data
    """
    # Get color palette
    palette = get_palette(n=n_colors, palette_name=palette_name, saturation=saturation)
    
    # Set font family and size
    plt.rcParams['font.family'] = font_family
    plt.rcParams['font.size'] = font_size
    
    metrics = {'setup': ['reward', 'distance'],
               'strategic_choices': ['buyer stage 1', 'seller stage 2'], 
               'results': ['buyer stage 3', 'utility']}
    
    x_labels = ['apple', 'orange']

    for key, metric in metrics.items():
         # Create figure 
        fig, ax = plt.subplots(1, 2, figsize=(width, height)) 
        # loop over rows and columns
        for i in range(2):
            # set x labels
            if key == 'results' and i == 1:
                x_labels = ['buyer', 'seller']
            # get data
            if key == 'setup':
                if i == 0:
                    bar_1 = data['reward_apple']
                    bar_2 = data['reward_orange']
                if i == 1:
                    bar_1 = data['distance_apple']
                    bar_2 = data['distance_orange']
            if key == 'strategic_choices':
                if i == 0:
                    if data['buyer_choice_stage_1'] == 'apple':
                        bar_1 = 10
                        bar_2 = 0
                    else:
                        bar_1 = 0
                        bar_2 = 10
                if i == 1:
                    bar_1 = data['price_apple_stage_2']
                    bar_2 = data['price_orange_stage_2']
            if key == 'results':
                if i == 0:
                    if data['buyer_choice_stage_3'] == 'apple':
                        bar_1 = 10
                        bar_2 = 0
                    else:
                        bar_1 = 0
                        bar_2 = 10
                if i == 1:
                    bar_1 = data['buyer_overall_utility']
                    bar_2 = data['seller_utility']
            ax[i].bar(x_labels, [float(bar_1), float(bar_2)], color=palette,  zorder=1)
            ax[i].set_ylabel(metric[i])
            ax[i].yaxis.grid(True, linestyle='-', which='major', color='lightgrey', alpha=0.5, zorder=-100)
            ax[i].set_ylim(-0.5, 11)
            if key == 'strategic_choices' and i == 0:
                ax[i].set_yticks([0, 10])
                ax[i].set_yticklabels([0, 1])
            if key == 'results' and i == 0:
                ax[i].set_yticks([0, 10])
                ax[i].set_yticklabels([0, 1])
            # customize patches
            for patch in ax[i].patches:
                bb = patch.get_bbox()
                color = patch.get_facecolor()
                p_bbox = get_fancy_bbox(bb, "round,pad=-0.0025,rounding_size=0.02", color, mutation_aspect=5)
                # remove the original patch and add the new one
                patch.remove()
                ax[i].add_patch(p_bbox)
        fig.tight_layout()
        # ax.set_xticklabels(x + 1)
        sns.despine(left=True, bottom=False)
        
        # save plots 
        plt.savefig(f'{data_directory}/{sim_name}_id_{sim_id}_run_{run}_{key}.pdf', bbox_inches='tight')
        plt.savefig(f'{data_directory}/{sim_name}_id_{sim_id}_run_{run}_{key}.jpg', bbox_inches='tight')

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

    # x-axis
    plt.xlabel('Runs')
    ax.set_xticks(x)
    ax.set_xticklabels(x + 1)
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
                  set(data['metric']),
                  title=legend_title, 
                  frameon=False,
                  ncol=1, 
                  bbox_to_anchor=bbox_to_anchor,
                  loc=legend_loc)
    # save plots 
    plt.savefig(f'{data_directory}/{sim_name}_id_{sim_id}_main_res.pdf', bbox_inches='tight')
    plt.savefig(f'{data_directory}/{sim_name}_id_{sim_id}_main_res.jpg', bbox_inches='tight') # for demo in browser