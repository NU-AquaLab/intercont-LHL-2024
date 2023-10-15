import pandas as pd

from lhledge.helpers import alpha3_to_alpha2

def load_inter_country_distances(cepii_filename, min_dist_filename):

    cepii = pd.read_csv(cepii_filename)
    min_dists = pd.read_csv(min_dist_filename)

    cepii["cc_src"] = cepii["iso_o"].map(alpha3_to_alpha2)
    cepii["cc_dst"] = cepii["iso_d"].map(alpha3_to_alpha2)
    min_dists["cc_src"] = min_dists["iso_o"].map(alpha3_to_alpha2)
    min_dists["cc_dst"] = min_dists["iso_d"].map(alpha3_to_alpha2)

    cepii = cepii[["cc_src", "cc_dst", "dist"]].join(
        min_dists[["cc_src", "cc_dst", "dist"]].set_index(["cc_src", "cc_dst",]),
        on=["cc_src", "cc_dst", ],
        how='left',
        lsuffix='_cepii',
        rsuffix='_min'
    )
    cepii["dist"] = cepii[["dist_cepii", "dist_min"]].min(axis=1).values

    return cepii[["cc_src", "cc_dst", "dist"]]