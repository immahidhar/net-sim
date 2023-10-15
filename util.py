# Names: Sai Jyothi Attuluri, Sai Nikhil Gummadavelli

# util

import json
import socket

from dstruct import EthernetPacket, ArpPacket

# constants
DEBUG = False
SELECT_TIMEOUT = 1
BUFFER_LEN = 1024
SL_TIMEOUT = 30 # in seconds
SL_REFRESH_PERIOD = 10 # in seconds
STATION_PQ_REFRESH_PERIOD = 1 # in seconds
CLIENT_CONNECT_RETRIES = 5
LOCAL_BROADCAST_MAC = "ff:ff:ff:ff:ff:ff"
PACKET_END_CHAR = '\?'

def isIp(s: str):
    """
    check if given string is ip address or not
    """
    if s.__contains__('.'):
        if s.count('.') == 3:
            return True
    return False

def sendArpReq(ipPack, stationChosen, nextHopIpaddress):
    """
    send ARP request
    """
    arpReq = ArpPacket(True, stationChosen.interface.ip, stationChosen.interface.mac, nextHopIpaddress, "")
    ethArpPack = EthernetPacket("", stationChosen.interface.mac, "ARP", arpReq.__dict__)
    ethArpPackDict = ethArpPack.__dict__
    if DEBUG:
        print(ethArpPackDict)
    data = json.dumps(ethArpPackDict)
    stationChosen.send(data)

def unpack(obj, d=None):
    """
    upack - deserialize object
    """
    if d is not None:
        for key, value in d.items():
            setattr(obj, key, value)
    return obj

def is_socket_invalid(sock) -> bool:
    """
    check if client socket active
    """
    try:
        # this will try to read bytes without blocking and also without removing them from buffer (peek only)
        data = sock.recv(16, socket.MSG_DONTWAIT | socket.MSG_PEEK)
        if len(data) == 0:
            return True
    except BlockingIOError:
        return False  # socket is open and reading from it would block
    except ConnectionResetError:
        return True  # socket was closed for some other reason
    except Exception as e:
        # print("unexpected exception when checking if a socket is closed")
        return True
    return False

def sendMac(nextHopIpaddress, stationChosen, ipPack):
    """
    send ipack to mac layer to send the packet to next hop
    """
    destinationMac = ""
    # check if we know the MAC address of nextHop ip address - arpCache
    if nextHopIpaddress == "0.0.0.0":
        nextHopIpaddress = ipPack.destIp
    else:
        if stationChosen.arpCache.__contains__(nextHopIpaddress):
            destinationMac = stationChosen.arpCache[nextHopIpaddress].mac

    # wrap message - ethernetPacket and put it in queue
    ethIpPack = EthernetPacket(destinationMac, stationChosen.interface.mac, "IP", ipPack.__dict__)
    stationChosen.pendQ.append(ethIpPack)

    if destinationMac == "":
        # send ARP req to bridge
        sendArpReq(ipPack, stationChosen, nextHopIpaddress)

def getNextRoute(rTable, dstIp):
    """
    get next hop ip address route for the destination ip address based on routing table
    """
    finalRoute = None
    defaultRoute = None
    # check rTable for destination network prefix
    # 0.0.0.0 is default route
    for route in rTable:
        if route.destSubnet == "0.0.0.0":
            defaultRoute = route
    # find the closest match among others based on subnet
    ipNums = list(map(int, dstIp.split(".")))
    # print(ipNums)
    routeMap = {}
    for route in rTable:
        dstNetPrx = route.destSubnet
        dstNetMsk = route.snMask
        dstNetPrxNums = list(map(int, dstNetPrx.split(".")))
        dstNetMskNums = list(map(int, dstNetMsk.split(".")))
        # print(ipNums, dstNetPrxNums)
        # check same subnet first
        ipAndVals = []
        dstAndVals = []
        for i in range(ipNums.__len__()):
            ipAndVals.append(ipNums[i] & dstNetMskNums[i])
            dstAndVals.append(dstNetPrxNums[i] & dstNetMskNums[i])
        if ipAndVals == dstAndVals:
            orValue = []
            for i in range(ipNums.__len__()):
                orValue.append(ipNums[i] & dstNetPrxNums[i])
            # print(orValue)
            orValueTotal = orValue[0] * 1000000000 + orValue[1] * 1000000 + orValue[2] * 1000 + orValue[3]
            routeMap[orValueTotal] = route
    biggestTotal = 0
    for total in routeMap:
        if total >= biggestTotal:
            biggestTotal = total
    finalRoute = routeMap[biggestTotal]
    if DEBUG:
        print(finalRoute)
    if finalRoute is not None:
        return finalRoute
    else:
        return defaultRoute
