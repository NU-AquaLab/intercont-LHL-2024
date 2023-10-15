import pycountry as pc
import pycountry_convert as pcc

# LHL_THRESHOLD = 47
LHL_THRESHOLD = 57
SoL_TH = 100
K = 0.75



# def filter_no_theshold(cepii, geoloc_hops, lhl_threshold=LHL_THRESHOLD):

#     # agrego CEPII y elimino cortos

#     geoloc_hops["near_side_cont"] = geoloc_hops["near_side_cc"].map(_get_continent)
#     geoloc_hops["far_side_cont"] = geoloc_hops["far_side_cc"].map(_get_continent)

#     tmp = geoloc_hops.loc[(geoloc_hops["near_side_cont"]
#                            != geoloc_hops["far_side_cont"])
#                            & (geoloc_hops["near_side_cc"] != "??")
#                            & (geoloc_hops["far_side_cc"] != "??")] \
#             [["near_side_cc", "far_side_cc",
#               "near_node_id", "far_node_id",
#               "near_node_asn", "far_node_asn",
#               "near_side_lat", "far_side_lat",
#               "near_side_lon", "far_side_lon",
#               "diff_rtt", "mpls_tunnel"]]

#     tmp = tmp.groupby(["near_side_cc", "far_side_cc",
#                        "near_node_id", "far_node_id",
#                        "near_side_lat", "far_side_lat",
#                        "near_side_lon", "far_side_lon",
#                        "near_node_asn", "far_node_asn",
#                        "mpls_tunnel"]) \
#         .min()["diff_rtt"] \
#         .reset_index()

#     tmp = tmp.join(
#         cepii[["cc_src", "cc_dst", "dist"]].set_index(["cc_src", "cc_dst"]),
#         on=["near_side_cc", "far_side_cc"],
#         how='left',
#         lsuffix='_left',
#         rsuffix='_right'
#     )

#     tmp = tmp.loc[(tmp["diff_rtt"] > ((tmp["dist"]) / (SoL_TH)))]
#     return tmp

# def filter_no_geoloc(cepii, geoloc_hops, lhl_threshold=LHL_THRESHOLD):

#     geoloc_hops["near_side_cont"] = geoloc_hops["near_side_cc"].map(_get_continent)
#     geoloc_hops["far_side_cont"] = geoloc_hops["far_side_cc"].map(_get_continent)

#     tmp = geoloc_hops.loc[(geoloc_hops["diff_rtt"] > lhl_threshold)] \
#             [["near_side_cc", "far_side_cc",
#               "near_node_id", "far_node_id",
#               "near_node_asn", "far_node_asn",
#               "near_side_lat", "far_side_lat",
#               "near_side_lon", "far_side_lon",
#               "diff_rtt", "mpls_tunnel"]]

#     tmp = tmp.groupby(["near_side_cc", "far_side_cc",
#                        "near_node_id", "far_node_id",
#                        "near_side_lat", "far_side_lat",
#                        "near_side_lon", "far_side_lon",
#                        "near_node_asn", "far_node_asn",
#                        "mpls_tunnel"]) \
#         .min()["diff_rtt"] \
#         .reset_index()

#     tmp = tmp.join(
#         cepii[["cc_src", "cc_dst", "dist"]].set_index(["cc_src", "cc_dst"]),
#         on=["near_side_cc", "far_side_cc"],
#         how='left',
#         lsuffix='_left',
#         rsuffix='_right'
#     )

#     tmp = tmp.loc[(tmp["diff_rtt"] > ((tmp["dist"]) / (SoL_TH)))]
#     return tmp

def _get_continent(cc):
    if cc == "":
        return ""

    try:
        country = pc.countries.get(alpha_2=cc)
        continent = pcc.country_alpha2_to_continent_code(country.alpha_2)
        return continent
    except:
        return ""

def filter_with_cepii(cepii, geoloc_hops, lhl_threshold=LHL_THRESHOLD):

    # agrego CEPII y elimino cortos

    geoloc_hops["near_side_cont"] = geoloc_hops["near_side_cc"].map(_get_continent)
    geoloc_hops["far_side_cont"] = geoloc_hops["far_side_cc"].map(_get_continent)

    tmp = geoloc_hops.loc[(geoloc_hops["diff_rtt"] > lhl_threshold) \
                    & (geoloc_hops["near_side_cont"]
                       != geoloc_hops["far_side_cont"])
                    & (geoloc_hops["near_side_cc"] != "??")
                    & (geoloc_hops["far_side_cc"] != "??")] \
            [["near_side_cc", "far_side_cc",
              "near_node_id", "far_node_id",
              "near_node_asn", "far_node_asn",
              "near_side_lat", "far_side_lat",
              "near_side_lon", "far_side_lon",
              "diff_rtt", "mpls_tunnel"]]

    tmp = tmp.groupby(["near_side_cc", "far_side_cc",
                       "near_node_id", "far_node_id",
                       "near_side_lat", "far_side_lat",
                       "near_side_lon", "far_side_lon",
                       "near_node_asn", "far_node_asn",
                       "mpls_tunnel"]) \
        .min()["diff_rtt"] \
        .reset_index()

    tmp = tmp.join(
        cepii[["cc_src", "cc_dst", "dist"]].set_index(["cc_src", "cc_dst"]),
        on=["near_side_cc", "far_side_cc"],
        how='left',
        lsuffix='_left',
        rsuffix='_right'
    )

    # Cond 1: no violation of speed of light contrains
    # Cond 2: No long detours. Latency can't be twice the inter-country distance
    # tmp = tmp.loc[(tmp["diff_rtt"] > ((1 * tmp["dist"]) / (SoL_TH)))
    #                & ((tmp["diff_rtt"]  * SoL_TH) < (2 * tmp["dist"]))]
    tmp = tmp.loc[(tmp["diff_rtt"] > ((tmp["dist"]) / (SoL_TH)))]
    return tmp

def find_min_rtt(lhl):

    _geoloc_hops = lhl.drop_duplicates(["near_side_addr", "far_side_addr"]) \
                          .loc[ (lhl["far_side_rtt"] >  lhl["near_side_rtt"])] \
                          [["near_side_addr", "far_side_addr",
                            "near_side_rdns", "far_side_rdns",
                            "near_node_id", "far_node_id",
                            "near_side_cc", "far_side_cc",
                            "near_side_lat", "far_side_lat",
                            "near_side_lon", "far_side_lon",
                            "near_node_asn", "far_node_asn",]]

    min_near = lhl.groupby(["near_side_addr", "far_side_addr"])["near_side_rtt"] \
        .min() \
        .reset_index()

    min_far = lhl.groupby(["near_side_addr", "far_side_addr"])["far_side_rtt"] \
        .min() \
        .reset_index()

    mpls = lhl.groupby(["near_side_addr", "far_side_addr"])["mpls_tunnel"] \
        .max() \
        .reset_index()

    _geoloc_hops = _geoloc_hops.join(
        min_near.set_index(["near_side_addr", "far_side_addr"]),
        on=["near_side_addr", "far_side_addr"],
        how='left',
        lsuffix='_left',
        rsuffix='_right'
    )

    _geoloc_hops = _geoloc_hops.join(
        min_far.set_index(["near_side_addr", "far_side_addr"]),
        on=["near_side_addr", "far_side_addr"],
        how='left',
        lsuffix='_left',
        rsuffix='_right'
    )
    
    _geoloc_hops = _geoloc_hops.join(
        mpls.set_index(["near_side_addr", "far_side_addr"]),
        on=["near_side_addr", "far_side_addr"],
        how='left',
        lsuffix='_left',
        rsuffix='_right'
    )


    _geoloc_hops["diff_rtt"] = _geoloc_hops["far_side_rtt"] - _geoloc_hops["near_side_rtt"]

    _geoloc_hops = _geoloc_hops.loc[(_geoloc_hops["near_side_cc"].notnull())
                                    & (_geoloc_hops["far_side_cc"].notnull())]


    return _geoloc_hops
