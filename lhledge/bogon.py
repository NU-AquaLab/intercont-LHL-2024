import radix

NOT_FOUND = 0

class bogonDetector:
    def __init__(self):
        self.rtree = radix.Radix()
        
        rnode = self.rtree.add("10.0.0.0/8")
        rnode.data["rfc"] = "rfc1918"
        rnode = self.rtree.add("172.16.0.0/12")
        rnode.data["rfc"] = "rfc1918"
        rnode = self.rtree.add("192.168.0.0/16")
        rnode.data["rfc"] = "rfc1918"

        rnode = self.rtree.add("100.64.0.0/10")
        rnode.data["rfc"] = "rfc6598"

        rnode = self.rtree.add("224.0.0.0/4")
        rnode.data["rfc"] = "multicast"

        rnode = self.rtree.add("169.254.0.0/16")
        rnode.data["rfc"] = "link-local address"

        # not found
        rnode = self.rtree.add("0.0.0.0/0")
        rnode.data["rfc"] = NOT_FOUND

    def isBogon(self, addr):
        return self.rtree.search_best(addr).data["rfc"] != NOT_FOUND

    def findRFC(self, addr):
        return self.rtree.search_best(addr).data["rfc"]