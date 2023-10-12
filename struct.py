# Names: Sai Jyothi Attuluri, Sai Nikhil Gummadavelli

# struct - Data structures

class Interface:
    """
    Interface
    """
    def __init__(self, name, ip, snMask, mac, lan):
        self.name: str = name
        self.ip: str = ip
        self.snMask: str = snMask
        self.mac: str = mac
        self.lan: str = lan

    def __str__(self):
        return ("name: \'" + self.name + "\', ip: \'" + self.ip + "\', snMask: \'"+ self.snMask
                + "\', mac: \'" + self.mac + "\', lan: \'"+ self.lan+ "\'")

class RoutingTable:
    """
    Routing Table
    """
    def __init__(self, destinationSubnet, nextHop, snMask, ifaceName):
        self.destinationSubnet = destinationSubnet
        self.nextHop = nextHop
        self.snMask = snMask
        self.ifaceName: str = ifaceName

    def __str__(self):
        return ("destinationSubnet: \'" + self.destinationSubnet + "\', nextHop: \'" + self.nextHop
                + "\', snMask: \'" + self.snMask + "\', ifaceName: \'" + self.ifaceName + "\'")

class Packet:
    """
    Packet
    """
    def __int__(self):
        self.size: int = 0 # size of the packet


class IpPacket(Packet):
    """
    IpPacket
    """

class EthernetPacket(IpPacket):
    """
    Ethernet Packet
    """
