import geoip2.database

class MaxMindGeolocator():
    def __init__(self, filename):
        # self.geo = geoip2.database.Reader('GeoLite2-City.mmdb')
        self.geo = geoip2.database.Reader(filename)
    def geolocate(self, addr):
        try:
            response = self.geo.city(addr)
            # print(response)
            # "near_side_geoloc": {"contient": "***", "cc": "DK", "region": "***", "city": "***", "lat": 55.6761, "lon": 12.5683},
            cc = {
                "contient": "***",
                "cc": response.country.iso_code,
                "city": "***",
                "lat": response.location.latitude,
                "lon": response.location.longitude,
                "method": "maxmind"
            }
        except:
            cc = {"cc": "??", "method": "maxmind"}
        
        return cc