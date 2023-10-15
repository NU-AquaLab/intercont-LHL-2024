import os.path
import os

def _create_dir(filename):

    dir_to_create = "/".join(filename.split("/")[:-1])

    if not os.path.exists('{}'.format(dir_to_create)):
        try:
            os.makedirs('{}'.format(dir_to_create))
        except:
            print("Dir exists")

    return None

def get_ripe_raw_metadata_filename(cfg, yyyy, mm, dd):
    filename = cfg["paths"]["raw-metadata"].format(yyyy, mm, dd)
    _create_dir(filename)
    return filename

def get_ripe_cleaned_metadata_filename(cfg, dt, cc):
    filename = cfg["paths"]["cleaned-metadata"].format(cc, cc, dt.year, dt.month, dt.day)
    _create_dir(filename)
    return filename

def _generate_traceroute_measurements_filename(cfg, cc, dt, msm_id, i):
    filename = cfg["paths"]["atlas-traceroute-measurements"].format(
        cc,
        dt.strftime("%Y-%m-%d"), 
        dt.strftime("%H"), 
        msm_id,
        i
    )
    _create_dir(filename)
    return filename


def generate_rtt_traceroute_timeseries_data(cfg, cc, dt, probe_id):
    filename = cfg["paths"]["rtt-traceroute-timeseries-data"].format(
        cc,
        dt.strftime("%Y-%m-%d"), 
        probe_id
    )
    _create_dir(filename)
    return filename


def generate_viz_rtt_traceroute_filename(cfg, cc, prb_id, date_start, date_end):
    filename = cfg["paths"]["viz-rtt-traceroute-timeseries"].format(
        cc,
        prb_id,
        prb_id,
        date_start.strftime("%Y-%m-%d"), 
        date_end.strftime("%Y-%m-%d"), 
    )
    _create_dir(filename)
    return filename
