# Names: Sai Jyothi Attuluri, Sai Nikhil Gummadavelli

# struct - Data structures

class Interface:
    """
    Interface
    """
    def __init__(self, name: str, ip: str, snMask: str, mac: str, lan: str):
        self.name = name
        self.ip = ip
        self.snMask = snMask
        self.mac = mac
        self.lan = lan

    def __str__(self):
        return ("name: \'" + self.name + "\', ip: \'" + self.ip + "\', snMask: \'"+ self.snMask
                + "\', mac: \'" + self.mac + "\', lan: \'"+ self.lan+ "\'")

class RoutingTable:
    """
    Routing Table
    """
    def __init__(self, destinationSubnet: str, nextHop: str, snMask: str, ifaceName: str):
        self.destinationSubnet = destinationSubnet
        self.nextHop = nextHop
        self.snMask = snMask
        self.ifaceName = ifaceName

    def __str__(self):
        return ("destinationSubnet: \'" + self.destinationSubnet + "\', nextHop: \'" + self.nextHop
                + "\', snMask: \'" + self.snMask + "\', ifaceName: \'" + self.ifaceName + "\'")

class Packet:
    """
    Packet
    """
    def __int__(self):
        self.size = 0 # size of the packet


class IpPacket(Packet):
    """
    IpPacket
    """

class EthernetPacket(IpPacket):
    """
    Ethernet Packet
    """
