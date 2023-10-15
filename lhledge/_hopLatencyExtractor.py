from pprint import pprint
import socket
from datetime import datetime, timedelta
import sqlite3
import time

import pandas as pd
import numpy as np
from adtk.detector import LevelShiftAD

class _hopLatencyExtractor(object):
    """docstring for longHaulDetector"""
    def __init__(self):
        super(_hopLatencyExtractor, self).__init__()
        
        self.rdns_dict = {}
        self.changepoints = {}

    #######

    ######

    def __epoch2dt(self, t_dict):
        _t = "{}.{}".format(t_dict["sec"], t_dict["usec"])
        return datetime.fromtimestamp(float(_t))

    def __cast_epoch(self, t_dict):
        _t = "{}.{}".format(t_dict["sec"], t_dict["usec"])
        return float(_t)

    def __get_rdns(self, addr):
        if addr not in self.rdns_dict.keys():
            try:
                self.rdns_dict[addr] = socket.getnameinfo((addr, 0), 0)[0]
            except:
                self.rdns_dict[addr] = addr
                
        return self.rdns_dict[addr]

    def __ripe_json2df(self, traceroute):
        df = pd.DataFrame()
        
        for result in traceroute:
            
            loop = pd.DataFrame(result["result"])
            
            # remove unresponded packet probes
            if "x" in list(loop):
                loop = loop.drop("x", 1)

            if "err" in list(loop):
                loop = loop[loop["err"].isnull()]
            
            if loop.size > 0 and ("rtt" in list(loop)) and ("from" in list(loop)):

                loop = loop[["from", "rtt"]].sort_values("rtt").iloc[0]
                loop["hop"] = result["hop"]
                # loop["hop"] = loop["hop"].astype(int)

                df = pd.concat([df, loop])

        if df.size > 0:
            df = df.reset_index()
            df = df[["from", "hop", "rtt"]]
            # reformatting naming convention to match with CAIDA's 
            df.columns = ["addr", "probe_ttl", "rtt"]

        return df

    def _computeInterhopLatencyBase(self, df, dst, src):


        if df.shape[0] > 2:

            key = f"{src} > {dst}"
            if key not in self.changepoints.keys():
                self.changepoints[key] = []

            rows = np.arange(1, df.shape[0])
            idx = rows[df["probe_ttl"][1:].values - df["probe_ttl"][:-1].values == 1]
            # print(df)
            # print(df["probe_ttl"][1:].values - df["probe_ttl"][:-1].values == 1)
            # print(idx)

            for i in idx:

                if df["probe_ttl"][i - 1] + 1 == df["probe_ttl"][i]:
                
                    rdns0 = self.__get_rdns(df["addr"][i - 1])
                    rdns1 = self.__get_rdns(df["addr"][i])

                    if "icmpext" in list(df):
                        if df["icmpext"].isnull()[i]:
                            mpls_tunnel = False
                        else:
                            mpls_tunnel = True
                    else:
                        mpls_tunnel = False


                    long_haul_link = {
                        "near_side_addr": df["addr"][i - 1],
                        "far_side_addr": df["addr"][i],
                        "near_side_rtt": df["rtt"][i - 1],
                        "far_side_rtt": df["rtt"][i],
                        "near_side_ttl": int(df["probe_ttl"][i - 1]),
                        "far_side_ttl": int(df["probe_ttl"][i]),
                        "consecutive_hops": bool(df["probe_ttl"][i - 1] + 1 == df["probe_ttl"][i]),
                        "near_side_rdns": rdns0,
                        "far_side_rdns": rdns1,
                        "near_side_timestamp": float(df["timestamp"][i - 1]),
                        "far_side_timestamp": float(df["timestamp"][i]),
                        "mpls_tunnel": bool(mpls_tunnel),
                    }

                    self.changepoints[key].append(long_haul_link)

        return
    
    def __accomodate_scamper(self, traceroute):

        df = pd.DataFrame(traceroute["hops"])
        df = df.reset_index()

        # some old versions of scamper did not per-hop stamp tx values on traceroute measurements
        if "tx" in list(df):
            df["timestamp"] = df["tx"].apply(self.__cast_epoch)
        else:
            df["timestamp"] = np.repeat(int(traceroute["start"]["sec"]), df.shape[0])

        return df

    def computeInterhopLatencyBase(self, traceroute, platform="ripe"):
        
        if platform == "ripe":
            df = self.__ripe_json2df(traceroute["result"])
            dst = traceroute["dst_addr"]
            df["timestamp"] = np.repeat(int(traceroute["timestamp"]), df.shape[0])
            # for ripe measurements this point is crucial because the platform can 
            # schedule mesurements from multiple probes to **a** target destination
            src = traceroute["src_addr"]
        elif platform == "ark":
            df = self.__accomodate_scamper(traceroute)
            dst = traceroute["dst"]
            # To be filled
            src = traceroute["src"]
        else:
            return

        # Ensures that it is not an empty measurement
        if df.size > 0:
            # ADTK only works with time series so we do this work around
            base = datetime.today()
            date_list = [base - timedelta(days=x) for x in range(df.shape[0])]
            df["fake_date"] = date_list

            self._computeInterhopLatencyBase(df, dst, src)

        return

    def getAllLongHauls(self):
        return self.changepoints
