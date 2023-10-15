from lhlcloud.maxmind import MaxMindGeolocator
from lhlcloud.hoiho import HoihoGeolocator

class geolocator():
    def __init__(self, maxmind_filename, hoiho_script, hoiho_file):
        self.mm = MaxMindGeolocator(maxmind_filename)
        self.hoiho = HoihoGeolocator(hoiho_script, hoiho_file)
    def geolocate(self, addr, hostname):

        if (addr != hostname) and len(hostname) > 0:
            self.hoiho.geolocate(hostname)
            
            if self.hoiho.isCompleteRecord():

                cc = self.hoiho.getGeolocation()
                cc["method"] = "hoiho"

                return cc


        # in any other case
        cc = self.mm.geolocate(addr)

        return cc
