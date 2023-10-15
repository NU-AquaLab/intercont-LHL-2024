import subprocess

COMPLETE_RECORD = 6

class HoihoGeolocator:

    def __init__(self, hoiho_script, hoiho_file):

        self.hoiho_script = hoiho_script
        self.hoiho_file = hoiho_file

        # self.airports = Airports()
        

    def geolocate(self, hostname):
        p = subprocess.Popen(["perl", self.hoiho_script, self.hoiho_file, hostname], stdout=subprocess.PIPE)
        out, err = p.communicate()

        self.out = str(out)

    def isGeolocation(self):
        return len(self.out) > 0

    def isCompleteRecord(self):
        return len(self.out.split("\n")[0][:-1].split(" ")) == COMPLETE_RECORD

    def getGeolocation(self):

        elems = self.out.split("\n")[0].split(" ")

        record = {
            "code": elems[1],
            "cc": elems[2],
            "lat": float(elems[3]),
            "lon": float(elems[4]),
            "city": elems[5]
        }

        return record