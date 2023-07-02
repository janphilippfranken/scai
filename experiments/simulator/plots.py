from typing import (
    Optional, 
    Dict, 
    Any,
    List,
    Tuple,
)


import pandas as pd 

import colorsys
import seaborn as sns
import matplotlib.colors as mc
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


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
   
def plot_user_data(
    data: pd.DataFrame,
    metric: str = 'satisfaction',
    data_directory: str = 'sim_res', 
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
    y_label_coords: Tuple[float, float] = (-0.12, 0.525),
    y_ticks: List[int] = [0, 2, 4, 6, 8, 10],
    y_ticklabels: List[int] = [0, 2, 4, 6, 8, 10],
    y_lim: Tuple[float, float] = (0, 10),
    legend: bool = True,
    legend_title: str = 'User',
    legend_loc: str = 'center left',
    bbox_to_anchor: Tuple[float, float] = (1.05, 0.5),
) -> None:
    """
    Plot user data

    Args:   
        data (pd.DataFrame): user data
        data_directory (str, optional): directory to save the data. Defaults to 'sim_res'.
        sim_name (str, optional): simulation name. Defaults to 'sim_1'.
        sim_id (str, optional): simulation id. Defaults to '0'.
        palette (str, optional): color palette. Defaults to 'colorblind'.
        saturation (float, optional): saturation of the colors. Defaults to 0.6.
    """
    # Get color palette
    palette = get_palette(n=len(data['agent_id'].unique()), palette_name=palette_name, saturation=saturation)
    
    # Set font family and size
    plt.rcParams['font.family'] = font_family
    plt.rcParams['font.size'] = font_size

    # Create figure 
    fig, ax = plt.subplots(figsize=(width, height))

    # Store lines for legend
    lines = []  

    # Plot data
    for i, user in enumerate(data['agent_id'].unique()):
        x = data[data['agent_id'] == user]['epoch']
        y = data[data['agent_id'] == user][metric]
        color = palette[i]
        line = ax.plot(x, y, color=color, linewidth=linewidth, zorder=zorder)
        lines.append(line) 
        ax.scatter(x, y, color=[lighten_color(scatter_color)]*len(x))  

    # x-axis
    plt.xlabel('Epoch')
    sns.despine(left=True, bottom=False)
    
    # y-axis
    ax.set_ylabel(metric.capitalize())
    ax.yaxis.set_label_coords(*y_label_coords)
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_ticklabels)
    ax.yaxis.grid(True, linestyle='-', which='major', color='lightgrey', alpha=0.5, zorder=-100)
    plt.ylim(y_lim)

    # legend 
    if legend:
        ax.legend(lines, 
                  data['agent_id'].unique(), 
                  title=legend_title, 
                  frameon=False, 
                  ncol=1, 
                  bbox_to_anchor=bbox_to_anchor,
                  loc=legend_loc)
    
    # save plots 
    plt.savefig(f'{data_directory}/{sim_name}_{sim_id}.pdf', bbox_inches='tight')
    plt.savefig(f'{data_directory}/{sim_name}_{sim_id}.jpg', bbox_inches='tight') # for demo in browser