import networkx as nx
import numpy as np
import pandas as pd

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.patches import Circle

def create_slide(theta0, theta1, step=100):

    x = []
    y = []

    x.append(0)
    y.append(0)

    r = 1
    for theta in np.linspace(theta0, theta1, step):
        x.append(r * np.cos(theta))
        y.append(r * np.sin(theta))

    x.append(0)
    y.append(0)

    return x, y

def compute_angle(lat1, lon1, lat2, lon2):
    dx = lon2 - lon1
    dy = lat2 - lat1

    if dx == 0:
        return np.nan

    return np.arctan(dy / dx)

def find_fine_grained_angle(df):

    G = nx.from_pandas_edgelist(
       df,
        "near_node_id",
        "far_node_id",
    )

    nx.set_node_attributes(
        G,
        pd.Series(
            df["near_side_cc"].values,
            index=df["near_node_id"]
        ).to_dict(),
        'cc',
    )
    nx.set_node_attributes(
        G,
        pd.Series(
            df["far_side_cc"].values,
            index=df["far_node_id"]
        ).to_dict(),
        'cc',
    )

    nx.set_node_attributes(
        G,
        pd.Series(
            df["near_side_lat"].values,
            index=df["near_node_id"]
        ).to_dict(),
        'lat',
    )
    nx.set_node_attributes(
        G,
        pd.Series(
            df["far_side_lat"].values,
            index=df["far_node_id"]
        ).to_dict(),
        'lat',
    )

    nx.set_node_attributes(
        G,
        pd.Series(
            df["near_side_lon"].values,
            index=df["near_node_id"]
        ).to_dict(),
        'lon',
    )
    nx.set_node_attributes(
        G,
        pd.Series(
            df["far_side_lon"].values,
            index=df["far_node_id"]
        ).to_dict(),
        'lon',
    )


    l = []
    for node in G.nodes():
        for neighbor_id in G.neighbors(node):
            theta = compute_angle(
                G.nodes[node]["lat"], G.nodes[node]["lon"],
                G.nodes[neighbor_id]["lat"], G.nodes[neighbor_id]["lon"]
            )

            if theta != np.nan:
                l.append((node,
                          neighbor_id,
                          G.nodes[node]["cc"],
                          G.nodes[neighbor_id]["cc"],
                          theta))


    angles = pd.DataFrame(l, columns=["node1", "node2", "cc1", "cc2", "theta",])
    return angles


def draw_compass(s, cycle):

    _b = np.linspace(-np.pi, np.pi, 13)

    b = []
    step = (_b[1] - _b[0]) / 2.0
    for i in range(len(_b)):
        b.append(_b[i] - (step))

    b.append(_b[i] + step)

    _vals, intervals = np.histogram(np.append(s, np.append(s + np.pi, s - np.pi)), bins=b)

    max_val = max(_vals)

    # fig, ax = plt.subplots(1, figsize=(10, 10))
    fig, ax = plt.subplots(1, figsize=(10, 5))



    # Draw pizza slides
    rose_cmap = matplotlib.cm.get_cmap('Purples')

    log_max = np.log(max_val)
    intensity = np.log(_vals)

    for i in range(1, len(b)):
        x, y = create_slide(b[i - 1], b[i])
        ax.fill_between(x, y, 0, color=rose_cmap(intensity[i - 1] / log_max))
        ax.plot([0, x[1]], [0, y[1]], color="white", lw=1)

        # coordinates of the annotation
        r = 0.75
        theta = (b[i] + b[i - 1]) / 2.0
        x = (r * np.cos(theta))
        y = (r * np.sin(theta))
        # print(f"{_vals[i - 1]} {x} {y}")

        if  _vals[i - 1] == max_val:
            ax.annotate(
                f"{int(_vals[i - 1]) / int(sum(_vals[:6])):.2f}",
                ((x, y + 0.05)),
                fontsize=25,
                color="white",
                va='center',
                ha='center'
            )
        else:
            ax.annotate(
                f"{int(_vals[i - 1]) / int(sum(_vals[:6])):.2f}",
                ((x, y)),
                fontsize=25,
                color="white",
                va='center',
                ha='center'
            )

    # Draw circle grid
    for r in np.arange(0.1, 1.01, 0.1)[::-1]:
        drawObject = Circle((0, 0), radius=r,
                            fill=False, color="#aeaeae",
                            linestyle="dashed")
        ax.add_patch(drawObject)

    # Draw radius grid
    for theta in np.linspace(-np.pi, np.pi, 13):
        x = np.cos(theta)
        y = np.sin(theta)
        ax.plot([0, x], [0, y], color="#aeaeae", linestyle="dashed")

    coordinates = {
        "N-S": (0, 1),
        "E": (1, 0),
        "W": (-1, 0),
        "NNE-SSW": (np.cos(np.pi / 3), np.sin(np.pi / 3)),
        "ENE-WSW": (np.cos(np.pi / 6), np.sin(np.pi / 6)),
        "NNW-SSE": (-np.cos(np.pi / 3), np.sin(np.pi / 3)),
        "WNW-ESE": (-np.cos(np.pi / 6), np.sin(np.pi / 6)),
    }

    for c in coordinates:
        ax.annotate(
            f"{c}",
            coordinates[c],
            fontsize=25,
            color="black",
            va='center',
            ha='center'
        )

    # ax.set_title(cycle)
    ax.axis('off')
    ax.set_ylim(0, 1)

    fig.subplots_adjust(hspace=0)
    fig.tight_layout()
    fig.savefig(f"figures/lhls/compass_rose_{cycle}.pdf")
