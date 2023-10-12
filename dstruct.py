# Names: Sai Jyothi Attuluri, Sai Nikhil Gummadavelli

# dstruct - Data structures

from enum import Enum

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
    def __init__(self, destSubnet: str, nextHop: str, snMask: str, ifaceName: str):
        self.destSubnet = destSubnet
        self.nextHop = nextHop
        self.snMask = snMask
        self.ifaceName = ifaceName

    def __str__(self):
        return ("destSubnet: \'" + self.destSubnet + "\', nextHop: \'" + self.nextHop
                + "\', snMask: \'" + self.snMask + "\', ifaceName: \'" + self.ifaceName + "\'")

class PortDb:
    """
    self learning mac-port database for bridge
    """
    def __init__(self, mac: str, port: int, timestamp):
        self.mac = mac
        self.port = port
        self.timestamp = timestamp

    def __str__(self):
        return ("mac: \'" + self.mac + "\', port: \'" + str(self.port)
                + "\', timestamp: \'" + self.timestamp + "\'")

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
        self.req =  req # request = True, response = False
        self.srcIp = srcIp
        self.srcMac = srcMac
        self.destIp = destIp
        self.destMac = destMac

    def __str__(self):
        return ("req: \'" + str(self.req) + "\', srcIp: \'" + self.srcIp + "\', srcMac: \'"
                + self.srcMac + "\', destIp: \'" + self.destIp + "\', destMac: \'" + self.destMac + "\'")

class IpPacket(Packet):
    """
    IpPacket
    """

class EthernetPacket:
    """
    Ethernet Packet
    """
    class EthernetPayloadType(Enum):
        """
        Packet type
        """
        ARP = 1
        IP = 2

    def __init__(self, dstMac: str, srcMac: str, pType: EthernetPayloadType, payload: Packet):
        self.dstMac = dstMac
        self.srcMac = srcMac
        self.pType = pType
        self.payload = payload

    def __str__(self):
        return ("dstMac: \'" + self.dstMac + "\', srcMac: \'" + self.srcMac
                + "\', pType: \'" + self.pType.__str__() + "\'" + "\', payload: \'" + self.payload.__str__() + "\'")
