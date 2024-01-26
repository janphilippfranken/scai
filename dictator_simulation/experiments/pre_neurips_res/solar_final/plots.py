from typing import (
    List,
    Tuple,
)

import pandas as pd 
import numpy as np

import colorsys
import seaborn as sns
from matplotlib.axes import Axes
import matplotlib.colors as mc
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import matplotlib.ticker as ticker


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


def plot_results(
    n_runs: int, 
    directory: str,
    data: list,
    linewidth: int = 2,
    zorder: int = 1,
    scatter_color: str = 'black',
    font_family: str = 'Avenir',
    font_size: int = 34,
    y_label_coords: tuple = (-0.07, 0.5),
    y_ticks: list = [0, 0.2, 0.4, 0.6, 0.8, 1],
    y_ticklabels: list = [0, 20, 40, 60, 80, 100],
    y_lim: tuple = (-0.1, 1.1),
    legend: bool = True,
    legend_title: str = 'Agent',
    legend_loc: str = 'center left',
    bbox_to_anchor: tuple = (1.0, 0.6),
    xlabel='Meta-Prompt Iteration',
    ylabel='Average Proportion',
    title = "Average Proportion Proposed to Deciders by Different Dictators across Different Utilities",
    group_labels: list = ['altruistic', 'fair', 'selfish'],
                      ):

    # Palette and labels for different groups
    palette = sns.color_palette("colorblind", len(data))
    line_styles = ['dotted', 'dashdot']
    
    x = [f"{i+1}" for i in range(n_runs)]
    fig, ax = plt.subplots(figsize=(20, 10))
    
    color_legend_handles = []
    style_legend_handles = []
    
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
            
            # Create proxy artists for the legend
            if j == 0:
                color_legend_handles.append(plt.Line2D([0], [0], color=palette[i], lw=linewidth))
            if i == 0:
                style_legend_handles.append(plt.Line2D([0], [0], color='black', linestyle=line_styles[j], lw=linewidth))

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

    plt.title(title, fontsize=24, fontweight='bold')

    if legend:
        # Add the proxy artists to the legend
        combined_legend_handles = color_legend_handles + style_legend_handles
        combined_legend_labels = group_labels + ['Fixed', 'Flexible']
        legend = ax.legend(combined_legend_handles, combined_legend_labels, title=legend_title, 
                  frameon=False,
                  ncol=1, 
                  bbox_to_anchor=bbox_to_anchor,
                  loc=legend_loc,
                  fontsize=font_size,
                  title_fontsize=font_size)
        for handle in legend.legendHandles:
            handle.set_linewidth(6.0)

    fig.savefig(f'{directory}/plot.pdf', format='pdf')
    plt.show()
