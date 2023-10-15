import pyasn
import sqlite3

from lhledge import _identifyLongHauls

class longHaulDetector(_identifyLongHauls._longHaulDetector):
    """docstring for longHaulDetector"""
    def __init__(self, midar_database="", table_date=""):
        _identifyLongHauls._longHaulDetector.__init__(self)


        if len(midar_database) > 0:
            
            self.conn = sqlite3.connect(midar_database)
            self.c = self.conn.cursor()
            
            self.table_date = table_date

            self.alias_resolution = {}
            self.node2as_mapping = {}
            self.geoloc = {}

    def __get_node_coordinates(self, node):
        if node not in self.geoloc.keys():

            self.c.execute(f"SELECT * FROM geoloc_{self.table_date} WHERE node={node};")
            row = self.c.fetchall()

            if len(row) > 0:
                # node.geo N11:   SA  CO  34  Bogota  4.60971 -74.08175   7674366ddec
                self.geoloc[node] = {
                    "contient": row[0][1],
                    "cc": row[0][2],
                    "region": row[0][3],
                    "city": row[0][4],
                    "lat": row[0][5],
                    "lon": row[0][6],

                }
            else:
                self.geoloc[node] = {"cc": "??"}


        return self.geoloc[node]

    def __get_node_id(self, addr):
        if addr not in self.alias_resolution.keys():

            self.c.execute(f"SELECT * FROM midar_{self.table_date} WHERE ip='{addr}';")
            row = self.c.fetchall()

            if len(row) == 0:
                node_id = 0
            elif len(row) == 1:
                _id, _addr, node_id = row[0]
            else:
                node_id = 0
                raise Exception

            self.alias_resolution[addr] = node_id


        return self.alias_resolution[addr]

    def __node2as_mapping(self, node):
        if node not in self.node2as_mapping.keys():

            self.c.execute(f"SELECT asn FROM bdrmapit_{self.table_date} WHERE node={node};")
            row = self.c.fetchall()

            if len(row) == 0:
                node_asn = 0
            elif len(row) == 1:
                if len(row[0]) == 1:
                    node_asn = row[0][0]
                else:
                    node_asn = 0
            else:
                node_asn = 0
                raise Exception

            self.node2as_mapping[node] = node_asn

        return self.node2as_mapping[node]

    
    def detectLongHaul(self, traceroute, platform="ripe"):
        super().detectLongHaulBase(traceroute, platform)

    def expandLHLdata(self, alias_resolution=False, node2as_mapping=False, geoloc=False):

        for lhl_id in self.changepoints.keys():
            lhl_list = self.changepoints[lhl_id]

            for long_haul_link in lhl_list:

                if alias_resolution:
                    node0 = self.__get_node_id(long_haul_link["near_side_addr"])
                    node1 = self.__get_node_id(long_haul_link["far_side_addr"])

                    long_haul_link["near_node_id"] = node0
                    long_haul_link["far_node_id"] = node1

                if node2as_mapping:
                    node0_asn = self.__node2as_mapping(long_haul_link["near_node_id"])
                    node1_asn = self.__node2as_mapping(long_haul_link["far_node_id"])

                    long_haul_link["near_node_asn"] = node0_asn
                    long_haul_link["far_node_asn"] = node1_asn

                if geoloc:
                    long_haul_link["near_side_geoloc"] = self.__get_node_coordinates(long_haul_link["near_node_id"])
                    long_haul_link["far_side_geoloc"] = self.__get_node_coordinates(long_haul_link["far_node_id"])
    
        # self.changepoints[key].append(long_haul_link)


    def getAllLongHauls(self):
        return self.changepoints
