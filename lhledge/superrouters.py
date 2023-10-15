import networkx as nx
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
import pycountry as pc

LHL_THREHOLD = 47

def find_super_routers(df):

    G = nx.from_pandas_edgelist(
        df.loc[(df["near_side_cc"] != "??" ) & (df["far_side_cc"] != "??" )],
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
            df["near_node_asn"].values,
            index=df["near_node_id"]
        ).to_dict(),
        'asn',
    )
    nx.set_node_attributes(
        G,
        pd.Series(
            df["far_node_asn"].values,
            index=df["far_node_id"]
        ).to_dict(),
        'asn',
    )

    l = []
    for node in G.nodes():
        s = set()
        for neighbor_id in G.neighbors(node):
            s.add(G.nodes[neighbor_id]["cc"])

        l.append((node, G.nodes[node]["cc"], G.nodes[node]["asn"], len(s), list(s)))

    superrouters = pd.DataFrame(l, columns=["router_id", "router_cc", "asn", "cc_cnt", "cc_list"])
    return superrouters.sort_values("cc_cnt", ascending=False)



def fix(x, y):
    d0 = y - x
    d1 = (180 - abs(y)) + (180 - abs(x))

    if d0 < d1:
        return [(x, y), ]
    elif y > x:
        return [(x, -180 - (180 - y)), (180 + (180 + x), y)]
    else:
#         return x, 180 + (180 + y)
        return [(x, 180 + (180 + y)), (-180 - (180 - x), y)]

def unfold(nlon, flon, nlat, flat):
    lons = fix(nlon, flon)

    return lons, [(nlat, flat)] * len(lons)

def plot_superrouters_map(near_node_id, _geoloc_hops, superrouters, lhl,
                          lakes_file="data/external/ne_10m_lakes/ne_10m_lakes.shx",
                          filename=""):

    router_cc = superrouters.loc[superrouters["router_id"] == near_node_id]["router_cc"].values[0]
    router_cc = pc.countries.get(alpha_2=router_cc).alpha_3

    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    lakes = gpd.read_file(lakes_file)
    #
    # Manual fixing
    # https://github.com/geopandas/geopandas/issues/1041
    world.loc[world['name'] == 'France', 'iso_a3'] = 'FRA'
    world.loc[world['name'] == 'Norway', 'iso_a3'] = 'NOR'
    world.loc[world['name'] == 'Somaliland', 'iso_a3'] = 'SOM'
    world.loc[world['name'] == 'Kosovo', 'iso_a3'] = 'RKS'
    #


    neighbors_id = np.unique(
        np.append(
            _geoloc_hops.loc[
                (_geoloc_hops["near_node_id"] == near_node_id)
                & (_geoloc_hops["diff_rtt"] > LHL_THREHOLD)
                & (_geoloc_hops["near_side_cc"] != _geoloc_hops["far_side_cc"])
            ]["far_node_id"].values,
            _geoloc_hops.loc[
                (_geoloc_hops["far_node_id"] == near_node_id)
                & (_geoloc_hops["diff_rtt"] > LHL_THREHOLD)
                & (_geoloc_hops["near_side_cc"] != _geoloc_hops["far_side_cc"])
            ]["near_node_id"].values,
        )
    )


    fig, ax = plt.subplots(1, figsize=(10, 6))

    world.plot(color='#dcdcdc', edgecolor='#555555', ax=ax)
    cc3_list = []

    for cc in superrouters.loc[superrouters["router_id"] == near_node_id]["cc_list"].values[0]:
        if str(cc) != "nan":
            cc3_list.append(pc.countries.get(alpha_2=cc).alpha_3)


    world.plot(color='#dcdcdc', edgecolor='#555555', ax=ax)
    world.loc[world["iso_a3"].isin(cc3_list)].plot(color='#828282',
                                                   edgecolor='#555555',
                                                   ax=ax)

    world.loc[world["iso_a3"] == router_cc].plot(color='#393939',
                                             edgecolor='#555555',
                                             ax=ax)
    lakes.plot(column='geometry', color='white', edgecolor='#555555', ax=ax, lw=0.1)


    routers_coordinates = lhl.loc[(lhl["near_node_id"] == near_node_id) & (lhl["far_node_id"].isin(neighbors_id))] \
        .drop_duplicates(["near_side_lon", "far_side_lon", "near_side_lat", "far_side_lat"]) \
        [["near_side_lon", "far_side_lon", "near_side_lat", "far_side_lat"]] \
        .values


    ax.scatter(
        routers_coordinates[:,0],
        routers_coordinates[:,2],
        color = "orange",
        s=35,
        edgecolor="k",
        lw=0.2,
        marker="o"
    )

    ax.scatter(
        routers_coordinates[:,1],
        routers_coordinates[:,3],
        color = "gold",
        s=25,
        edgecolor="k",
        lw=0.2,
        marker="*"
    )


    # for idx, row in lhl.loc[lhl["near_node_id"] == near_node_id] \
    #         .drop_duplicates(["near_side_lon", "far_side_lon",
    #                           "near_side_lat", "far_side_lat"]) \
    #         .iterrows():

    #     lons, lats = unfold(row["near_side_lon"], row["far_side_lon"],
    #                         row["near_side_lat"], row["far_side_lat"])

    #     for lon, lat in zip(lons, lats):
    #         ax.plot(
    #             [lon[0], lon[1]],
    #             [lat[0], lat[1]],
    #             color = "red",
    #             lw=0.1,
    #             alpha=0.5
    #         )

    for idx, row in lhl.loc[(lhl["near_node_id"] == near_node_id) 
                            & (lhl["far_side_cc"].isin(
                                superrouters.loc[superrouters["router_id"] == near_node_id]["cc_list"].values[0]
                                ))] \
            .drop_duplicates(["near_side_lon", "far_side_lon",
                              "near_side_lat", "far_side_lat"]) \
            .iterrows():

        lons, lats = unfold(row["near_side_lon"], row["far_side_lon"],
                            row["near_side_lat"], row["far_side_lat"])

        for lon, lat in zip(lons, lats):
            ax.plot(
                [lon[0], lon[1]],
                [lat[0], lat[1]],
                color = "red",
                lw=0.1,
                alpha=0.5
            )

    ax.set_xlim(-180, 180)
    ax.axis('off')

    fig.subplots_adjust(hspace=0)
    fig.tight_layout()
    if len(filename) > 0:
        fig.savefig(filename)


def plot_multiple_superrouters_map(near_node_id_list, _geoloc_hops, superrouters, lhl,
                                  lakes_file="data/external/ne_10m_lakes/ne_10m_lakes.shx",
                                  filename=""):

    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    lakes = gpd.read_file(lakes_file)
    #
    # Manual fixing
    # https://github.com/geopandas/geopandas/issues/1041
    world.loc[world['name'] == 'France', 'iso_a3'] = 'FRA'
    world.loc[world['name'] == 'Norway', 'iso_a3'] = 'NOR'
    world.loc[world['name'] == 'Somaliland', 'iso_a3'] = 'SOM'
    world.loc[world['name'] == 'Kosovo', 'iso_a3'] = 'RKS'
    #

    fig, ax = plt.subplots(1, figsize=(10, 6))

    world.plot(color='#dcdcdc', edgecolor='#555555', ax=ax)
    lakes.plot(column='geometry', color='white', edgecolor='#555555', ax=ax, lw=0.1)

    for near_node_id in near_node_id_list:

        neighbors_id = np.unique(
            np.append(
                _geoloc_hops.loc[
                    (_geoloc_hops["near_node_id"] == near_node_id)
                    & (_geoloc_hops["diff_rtt"] > LHL_THREHOLD)
                    & (_geoloc_hops["near_side_cc"] != _geoloc_hops["far_side_cc"])
                ]["far_node_id"].values,
                _geoloc_hops.loc[
                    (_geoloc_hops["far_node_id"] == near_node_id)
                    & (_geoloc_hops["diff_rtt"] > LHL_THREHOLD)
                    & (_geoloc_hops["near_side_cc"] != _geoloc_hops["far_side_cc"])
                ]["near_node_id"].values,
            )
        )

        cc3_list = []

        for cc in superrouters.loc[superrouters["router_id"] == near_node_id]["cc_list"].values[0]:
            if str(cc) != "nan":
                cc3_list.append(pc.countries.get(alpha_2=cc).alpha_3)

        
        world.loc[world["iso_a3"].isin(cc3_list)].plot(color='#828282',
                                                       edgecolor='#555555',
                                                       ax=ax)
        

        


        routers_coordinates = lhl.loc[(lhl["near_node_id"] == near_node_id) & (lhl["far_node_id"].isin(neighbors_id))] \
            .drop_duplicates(["near_side_lon", "far_side_lon", "near_side_lat", "far_side_lat"]) \
            [["near_side_lon", "far_side_lon", "near_side_lat", "far_side_lat"]] \
            .values


        ax.scatter(
            routers_coordinates[:,0],
            routers_coordinates[:,2],
            s=35,
            edgecolor="k",
            lw=0.2,
            marker="o"
        )

        ax.scatter(
            routers_coordinates[:,1],
            routers_coordinates[:,3],
            color = "gold",
            s=25,
            edgecolor="k",
            lw=0.2,
            marker="*"
        )


        for idx, row in lhl.loc[lhl["near_node_id"] == near_node_id] \
                .drop_duplicates(["near_side_lon", "far_side_lon",
                                  "near_side_lat", "far_side_lat"]) \
                .iterrows():

            lons, lats = unfold(row["near_side_lon"], row["far_side_lon"],
                                row["near_side_lat"], row["far_side_lat"])

            for lon, lat in zip(lons, lats):
                ax.plot(
                    [lon[0], lon[1]],
                    [lat[0], lat[1]],
                    color = "red",
                    lw=0.1,
                    alpha=0.5
                )

    ax.set_xlim(-180, 180)
    ax.axis('off')

    fig.subplots_adjust(hspace=0)
    fig.tight_layout()
    if len(filename) > 0:
        fig.savefig(filename)