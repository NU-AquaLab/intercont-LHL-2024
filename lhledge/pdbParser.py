import pandas as pd
import pycountry as pc
import pycountry_convert as pcc

def consolidate(fac, netfac, nets, orgs):
    footprint = fac.join(
        netfac.set_index(["fac_id", ]),
        on=["fac_id"],
        how='left',
        lsuffix='_left',
        rsuffix='_right'
    )

    footprint = footprint.join(
            nets.set_index(["net_id", ]),
            on=["net_id"],
            how='left',
            lsuffix='_left',
            rsuffix='_right'
        )

    footprint = footprint.join(
            orgs.set_index(["org_id", ]),
            on=["org_id"],
            how='left',
            lsuffix='_left',
            rsuffix='_right'
        )

    return footprint

def parse_facilities(pdb):
    fac = []

    for facility in pdb["fac"]["data"]:
        if (facility["longitude"] is not None):
            lon = float(facility["longitude"])
        else:
            lon = -90
        if (facility["latitude"] is not None):
            lat = float(facility["latitude"])
        else:
            lon = -180

        if (facility["country"] is not None) and (facility["id"] is not None):
            fac.append((int(facility["id"]), facility["name"],
                        facility["country"], lon, lat))

    return pd.DataFrame(fac, columns=["fac_id", "name", "cc", "lon", "lat"])

def parse_networks_at_facilities(pdb):
    netfac = []

    for net in pdb['netfac']["data"]:
        if (net["fac_id"] is not None) and (net["local_asn"] is not None):
            netfac.append((int(net["fac_id"]), int(net["local_asn"]), int(net["net_id"])))
    return pd.DataFrame(netfac, columns=["fac_id", "asn", "net_id"])

def parse_networks(pdb):
    nets = []
    for net in pdb['net']["data"]:
        if (net["id"] is not None) and (net["org_id"] is not None):
            nets.append((int(net["id"]), int(net["org_id"])))

    return  pd.DataFrame(nets, columns=["net_id", "org_id"])

def _get_continent(cc):
    if cc == "":
        return ""

    try:
        country = pc.countries.get(alpha_2=cc)
        continent = pcc.country_alpha2_to_continent_code(country.alpha_2)
        return continent
    except:
        return ""

def parse_orgs(pdb):
    orgs = []
    for org in pdb['org']["data"]:
        if (org["id"] is not None) and (org["country"] is not None):
            orgs.append((int(org["id"]), str(org["country"]),
                         _get_continent(str(org["country"]))))

    return pd.DataFrame(orgs, columns=["org_id", "org_cc", "org_continent"])

def parse(pdb):

    fac = parse_facilities(pdb)
    netfac = parse_networks_at_facilities(pdb)
    nets = parse_networks(pdb)
    orgs = parse_orgs(pdb)

    return consolidate(fac, netfac, nets, orgs)