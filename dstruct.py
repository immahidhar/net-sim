# Names: Sai Jyothi Attuluri, Sai Nikhil Gummadavelli

# dstruct - Data structures

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

class Route:
    """
    Routing Table
    """
    def __init__(self, destSubnet: str, nextHop: str, snMask: str, ifaceName: str):
        self.destSubnet = destSubnet
        self.nextHop = nextHop
        self.snMask = snMask
        self.ifaceName = ifaceName

    def __str__(self):
        return ("destSubnet: \'" + self.destSubnet + "\', nextHop: \'" + self.nextHop
                + "\', snMask: \'" + self.snMask + "\', ifaceName: \'" + self.ifaceName + "\'")

class ClientDb:
    """
    self learning mac-port database for bridge
    """
    def __init__(self, cliSock, timestamp):
        self.cliSock = cliSock
        self.timestamp = timestamp

    def __str__(self):
        return "cliSock: \'" + str(self.cliSock) + "\', timestamp: \'" + str(self.timestamp) + "\'"

class ArpDb:
    """
    Arp ip-mac database for station
    """
    def __init__(self, mac, timestamp):
        self.mac = mac
        self.timestamp = timestamp

    def __str__(self):
        return "mac: \'" + str(self.mac) + "\', timestamp: \'" + str(self.timestamp) + "\'"

class Packet:
    """
    Packet
    """
    def __init__(self, size: int, payload: str):
        self.size = size # size of the packet
        self.payload = payload

    def __str__(self):
        return "Packet(size: \'" + str(self.size) + "\', payload: \'" + self.payload + "\')"

class ArpPacket:
    """
    ARP Packet
    """
    def __init__(self, req: bool, srcIp: str, srcMac: str, destIp: str, destMac: str):
        self.type = ArpPacket.__name__
        self.req =  req # request = True, response = False
        self.srcIp = srcIp
        self.srcMac = srcMac
        self.destIp = destIp
        self.destMac = destMac

    def __str__(self):
        return ("ArpPacket(req: \'" + str(self.req) + "\', srcIp: \'" + self.srcIp + "\', srcMac: \'"
                + self.srcMac + "\', destIp: \'" + self.destIp + "\', destMac: \'" + self.destMac + "\')")

    def __repr__(self):
        return ("ArpPacket(req: \'" + str(self.req) + "\', srcIp: \'" + self.srcIp + "\', srcMac: \'"
                + self.srcMac + "\', destIp: \'" + self.destIp + "\', destMac: \'" + self.destMac + "\')")

class IpPacket:
    """
    IpPacket
    """
    def __init__(self, destIp: str, srcIp: str, prot: int, seq: int, payload):
        self.type = IpPacket.__name__
        self.destIp = destIp
        self.srcIp = srcIp
        self.prot = prot
        self.seq = seq
        self.payload = payload

    def __str__(self):
        return ("IpPacket(destIp: \'" + str(self.destIp) + "\', srcIp: \'" + self.srcIp + "\', prot: \'"
                + str(self.prot) + "\', seq: \'" + str(self.seq) + "\', payload: \'" + self.payload.__str__() + "\')")

class EthernetPacket:
    """
    Ethernet Packet
    """

    def __init__(self, dstMac: str, srcMac: str, pType: str, payload):
        self.type = EthernetPacket.__name__
        self.dstMac = dstMac
        self.srcMac = srcMac
        self.pType = pType
        self.payload = payload

    def __str__(self):
        return ("EthernetPacket(dstMac: \'" + self.dstMac + "\', srcMac: \'" + self.srcMac
                + "\', pType: \'" + self.pType.__str__() + "\'" + "\', payload: \'" + self.payload.__str__() + "\')")
