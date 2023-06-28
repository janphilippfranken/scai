import matplotlib.colors as mc
from matplotlib.patches import FancyBboxPatch
import colorsys
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FuncFormatter

def lighten_color(color, amount=0.5, desaturation=0.2):
    """
    Lightens and desaturates the given color by multiplying (1-luminosity) by the given amount
    and decreasing the saturation by the specified desaturation amount.
    Input can be matplotlib color string, hex string, or RGB tuple.
    Copy-pasted from Eric's slack.
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

def get_fancy_bbox(bb, boxstyle, color, background=False, mutation_aspect=3):
    """
    Creates a fancy bounding box for the bar plots. Adapted from Eric's function.
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
        zorder=2
    )

def change_saturation(rgb, change=0.6):
    """
    Changes the saturation of a color by a given amount. used .6 in marple-text for sns.colorblind pallette 
    """
    hsv = colorsys.rgb_to_hsv(rgb[0], rgb[1], rgb[2])
    saturation = max(0, min(hsv[1] * change, 1))
    return colorsys.hsv_to_rgb(hsv[0], saturation, hsv[2])

def get_ratings(df):
    """
    Returns a dataframe with the ratings for each user for plotting.
    """
    df_user = df[df['message_type'].str.contains('user') & df['rating'].notna()].copy()
    df_user['x'] = df_user.groupby('conversation_id').cumcount() + 1
    df_user['y'] = df_user['rating']
    # convert to int
    df_user['x'] = df_user['x'].astype(float)
    df_user['y'] = df_user['y'].astype(float)
    df_user['user_id'] = df_user['message_type']
    df_user['user_id'] = 'User ' + df_user['conversation_id'].astype(str)
    df_user = df_user[['x', 'y', 'user_id']]
    return df_user

def plot_user_ratings(df, palette=None, plot_dir=None, context_id=None, model=None, pdf=True):

    # TODO: make this flex, add pallete and user stuff to arguments
    change = 0.6 
    colorblind_palette = sns.color_palette("colorblind", 10)

    palette = {
        'User 1': change_saturation(colorblind_palette[0], change), 
        'User 2': change_saturation(colorblind_palette[1], change),      
        'User 3': change_saturation(colorblind_palette[2], change),
        'User 4': change_saturation(colorblind_palette[3], change),
    }

    plt.rcParams["font.family"] = "Avenir"
    plt.rcParams["font.size"] = 24

    fig, ax = plt.subplots(figsize=(10, 5))

    lines = []  # to store the lines for the legend

    for user in df['user_id'].unique():
        x = df[df['user_id'] == user]['x']
        y = df[df['user_id'] == user]['y'] 
        color = palette[user]
        line, = ax.plot(x, y, color=color, linewidth=2, zorder=1)  # Removed label from line
        lines.append(line)  # store the line for the legend
        scatter = ax.scatter(x, y, color=[lighten_color('black')]*len(x))  # Removed label from scatter

    # title
    plt.title('') # Adding Title
    
    # x axis
    plt.xticks(rotation=0)
    sns.despine(left=True, bottom=False)
    plt.xlabel('Epoch')

    # y axis
    ax.set_ylabel('Satisfaction')
    ax.yaxis.set_label_coords(-0.12, 0.525)
    ax.set_yticks([0, 2, 4, 6, 8, 10])
    ax.set_yticklabels([0, 2, 4, 6, 8, 10])
    ax.yaxis.grid(True, linestyle='-', which='major', color='lightgrey', alpha=0.5, zorder=-100)
    plt.ylim(0, 10.5)


    # legend 
    ax.legend(lines, df['user_id'].unique(), title='Users', frameon=False, ncol=1, 
              bbox_to_anchor=(1.05, 0.5), loc='center left')  
    
    # save
    if pdf:
        plt.savefig(f'{plot_dir}/{context_id}_{model}.pdf', bbox_inches='tight')
    else: 
        plt.savefig(f'{plot_dir}/{context_id}_{model}.jpg', bbox_inches='tight')