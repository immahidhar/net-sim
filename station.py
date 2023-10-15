# Names: Sai Jyothi Attuluri, Sai Nikhil Gummadavelli

# Station

import sys
import select
import signal
import threading

import json
import time

from client import Client
from dstruct import Interface, Route, IpPacket, ArpPacket, EthernetPacket, Packet, ArpDb
from util import SELECT_TIMEOUT, isIp, unpack, BUFFER_LEN, CLIENT_CONNECT_RETRIES, STATION_PQ_REFRESH_PERIOD, \
    getNextRoute, sendMac, sendArpReq, PACKET_END_CHAR, DEBUG, is_socket_invalid, SL_TIMEOUT, \
    SL_REFRESH_PERIOD


class Station(Client):
    """
    Station
    """

    def __init__(self, stationType, hosts, rTable, forwardQueue, interface: Interface):
        self.exitFlag = False
        self.stationType = stationType
        self.hosts = hosts
        self.rTable = rTable
        self.forwardQueue = forwardQueue
        self.interface = interface
        self.addrFileName = "." + self.interface.lan + '.addr'
        self.portFileName = "." + self.interface.lan + '.port'
        self.bridgePort = None
        self.bridgeHost = None
        self.getBridgeAddr()
        self.arpCache = {} # arp cache - (ip: str, arpDb: ArpDb)
        self.pendQ = [] # pending queue
        super().__init__(self.bridgeHost, self.bridgePort)

    def getBridgeAddr(self):
        try:
            with open(self.addrFileName, 'r') as addr:
                try:
                    self.bridgeHost = addr.readline()
                except:
                    print("error reading bridge ip address")
                    sys.exit(1)
            with open(self.portFileName, 'r') as port:
                try:
                    self.bridgePort = int(port.readline())
                except:
                    print("error reading bridge port")
                    sys.exit(1)
        except FileNotFoundError:
            print("no bridge with lan name", self.interface.lan, "found")
            # sys.exit(1)

    def start(self):
        """
        start station
        """
        if self.bridgeHost is None or self.bridgePort is None:
            return
        super().connect()
        if not self.validateBridgeAccept():
            return
        clientThread = threading.Thread(target=Client.run, args=(self,))
        pendQThread = threading.Thread(target=Station.checkOnPendingQueue, args=(self, ))
        # arpCleanUpThread = threading.Thread(target=Station.cleanUpArpCache, args=(self, ))
        # arpCleanUpThread.daemon = True
        pendQThread.daemon = True
        clientThread.start()
        pendQThread.start()
        # arpCleanUpThread.start()
        clientThread.join()

    def validateBridgeAccept(self):
        """
        check for accept/reject response
        """
        for i in range(CLIENT_CONNECT_RETRIES):
            try: # select()
                inputReady, outputReady, exceptReady = select.select([self.cliSock], [], [], SELECT_TIMEOUT)
            except select.error as e:
                if not self.exitFlag:
                    print("error on select", e)
                return False
            for sock in inputReady:
                if sock == self.cliSock:
                    try:  # recv()
                        data = self.cliSock.recv(BUFFER_LEN)
                    except OSError as e:
                        print("recv error ", e)
                        super().close(False)
                        return False
                    if not data:
                        if self.exitFlag:
                            return False
                        print("server closed connection",  self.server_addr)
                        super().close(False)
                        return False
                    else:
                        data = str(data, 'UTF-8').strip()
                        if data == "accept" + PACKET_END_CHAR:
                            print("bridge " + self.interface.lan + " accepted connection")
                            return True
                        elif data == "reject" + PACKET_END_CHAR:
                            print("bridge " + self.interface.lan + " rejected connection")
                            return False
                        else:
                            print(data)
                else:
                    print("Huh?")
                    pass
            return False

    def cleanUpArpCache(self):
        """
        clean up Arp cache once in a while
        """
        while not self.exitFlag:
            rmEntries = []
            for entry in self.arpCache:
                arpDb = self.arpCache[entry]
                currTime = time.time()
                oldTime = arpDb.timestamp
                if currTime - oldTime >= SL_TIMEOUT:
                    rmEntries.append(entry)
            for entry in rmEntries:
                self.arpCache.__delitem__(entry)
            time.sleep(SL_REFRESH_PERIOD)

    def processData(self, cliSock, dataBytes):
        """
        process data received
        :param cliSock:
        :param dataBytes:
        :return:
        """
        dataStrList = str(dataBytes, 'UTF-8')  # .strip()
        dataStrList = dataStrList.split(PACKET_END_CHAR)
        for dataStr in dataStrList:
            if dataStr == "":
                return
            if DEBUG:
                print(cliSock.getpeername(), " : ", dataStr)
            data = json.loads(dataStr) #.strip())
            # must have received Ethernet packet - unpack it
            ethPack = unpack(EthernetPacket("", "", "", ""), data)
            # print(cliSock.getpeername(), " : ", ethPack)
            packetType = ethPack.payload["type"]
            if packetType == ArpPacket.__name__:
                arpPack = ethPack.payload
                # check if this station is the destination station ip
                if arpPack["destIp"] == self.interface.ip:
                    # update arp cache from arp src
                    arpDb = ArpDb(arpPack["srcMac"], time.time())
                    self.arpCache[arpPack["srcIp"]] = arpDb
                    # check if ARP request or response
                    if arpPack["req"] is True:
                        # send ARP response back
                        self.sendARPResponse(arpPack)
            elif packetType == IpPacket.__name__:
                # process IP packet received
                ipPack = ethPack.payload
                # check if station is client or router
                if self.stationType == "-no":
                    # client
                    # check if this is the destination
                    if ipPack["destIp"] == self.interface.ip:
                        # get name of source ip and print it
                        srcIp = ipPack["srcIp"]
                        srcHostName = srcIp
                        for entry in self.hosts:
                            if srcIp == self.hosts[entry]:
                                srcHostName = entry
                                break
                        print(srcHostName + " >", ipPack["payload"]["payload"])
                    # else drop it
                else:
                    # figure out next hop ip address
                    nextRoute = getNextRoute(self.rTable, ipPack["destIp"])
                    nextHopIpaddress = nextRoute.nextHop
                    nextHopInterface = nextRoute.ifaceName
                    self.forwardQueue.append((nextHopInterface, nextHopIpaddress, ipPack))


    def sendARPResponse(self, arpReq):
        """
        send ARPResponse back
        """
        arpReq["destMac"] = self.interface.mac
        # create response - interchange source and destination
        arpRes = ArpPacket(False, arpReq["destIp"], arpReq["destMac"], arpReq["srcIp"], arpReq["srcMac"])
        ethArpPack = EthernetPacket(arpRes.destMac, self.interface.mac, "ARP", arpRes.__dict__)
        ethArpPackDict = ethArpPack.__dict__
        if DEBUG:
            print(ethArpPackDict)
        data = json.dumps(ethArpPackDict)
        self.send(data)

    def checkOnPendingQueue(self):
        """
        check if we can clear the pending queue
        """
        while not self.exitFlag:
            if self.pendQ.__len__() > 0:
                # check if we have new arp info
                for ethPack in self.pendQ:
                    # TODO: Bug here for ARP - 0.0.0.0
                    nextHopIpaddress = getNextRoute(self.rTable, ethPack.payload["destIp"]).nextHop
                    if nextHopIpaddress == "0.0.0.0":
                        nextHopIpaddress = ethPack.payload["destIp"]
                    if ethPack.dstMac == "":
                        if self.arpCache.__contains__(nextHopIpaddress):
                            # we have the mac now, fill it
                            arpDb = self.arpCache[nextHopIpaddress]
                            ethPack.dstMac = arpDb.mac
                        else:
                            # TODO: ARP
                            ipPackObj = unpack(IpPacket("", "", 0, 0, ""), ethPack.payload)
                            sendArpReq(ipPackObj, self, nextHopIpaddress)
                # check if we can send and clear any
                for i in range(self.pendQ.__len__()):
                    if self.pendQ.__getitem__(0).dstMac != "":
                        ethPack = self.pendQ.pop(0)
                        if DEBUG:
                            print(ethPack)
                        ethPackDict = ethPack.__dict__
                        data = json.dumps(ethPackDict)
                        self.send(data)
            time.sleep(STATION_PQ_REFRESH_PERIOD)

    def shutdown(self, exitFlag, shutdownFlag):
        """
        Shutdown station
        """
        super().close(shutdownFlag)
        if exitFlag:
            sys.exit(0)

class MultiStation:
    """
    MultiStation
    """

    def __init__(self, stationType, iFaceFileName, rTableFileName, hostsFileName):
        self.exitFlag = False
        self.numStations = 0
        self.stationType = stationType
        self.iFaceFileName = iFaceFileName
        self.rTableFileName = rTableFileName
        self.hostsFileName = hostsFileName
        self.forwardQueue = []
        self.hosts = {} # (iface, ip)
        self.rTable = []
        self.stations = []
        self.stationThreads = []
        self.loadHosts()
        self.loadRoutingTable()
        self.loadInterface()

    def loadInterface(self):
        """
        load multi station by reading interface file
        """
        try:
            with open(self.iFaceFileName, 'r') as iFaceFile:
                try:
                    iFaces = iFaceFile.readlines()
                    for iface in iFaces:
                        iface = iface.strip().split()
                        if len(iface) < 2:
                            break
                        # create a station
                        station = Station(self.stationType, self.hosts, self.rTable, self.forwardQueue,
                                          Interface(iface[0], iface[1], iface[2], iface[3], iface[4]))
                        # validate lan name before proceeding with station
                        if station.bridgeHost is None or station.bridgePort is None:
                            continue
                        self.stations.append(station)
                        self.numStations = self.numStations + 1
                except:
                    print("error reading interface file")
                    sys.exit(1)
        except FileNotFoundError as e:
            print(e)
            sys.exit(1)

    def loadHosts(self):
        """
        load hostname from hostname file
        """
        try:
            with open(self.hostsFileName, 'r') as hostsFile:
                try:
                    hosts = hostsFile.readlines()
                    for host in hosts:
                        host = host.strip().split()
                        if len(host) < 2:
                            break
                        self.hosts[host[0]] = host[1]
                except:
                    print("error reading hosts file")
                    sys.exit(1)
        except FileNotFoundError as e:
            print(e)
            sys.exit(1)

    def loadRoutingTable(self):
        """
        load routing table from rTable file
        """
        try:
            with open(self.rTableFileName, 'r') as rTableFile:
                try:
                    routes = rTableFile.readlines()
                    for route in routes:
                        route = route.strip().split()
                        if len(route) < 2:
                            break
                        self.rTable.append(Route(route[0], route[1], route[2], route[3]))
                except:
                    print("error reading hosts file")
                    sys.exit(1)
        except FileNotFoundError as e:
            print(e)
            sys.exit(1)

    def start(self):
        """
        start multi station
        """
        # start stations
        for station in self.stations:
            print("connecting to bridge lan", station.interface.lan)
            stationThread = threading.Thread(target=Station.start, args=(station,))
            self.stationThreads.append(stationThread)
            stationThread.daemon = True
            stationThread.start()

        if self.numStations > 1:
            routerThread = threading.Thread(target=MultiStation.routerForward, args=(self,))
            routerThread.daemon = True
            routerThread.start()

        for st in self.stationThreads:
            st.join()

    def routerForward(self):
        """
        forward packets this station is a router
        """
        if self.numStations == 1:
            return
        else:
            while not self.exitFlag:
                if self.forwardQueue.__len__() > 0:
                    (nextHopInterface, nextHopIpaddress, ipPack) = self.forwardQueue.pop(0)
                    ipPackObj = unpack(IpPacket("", "", 0, 0, ""), ipPack)
                    stationChosen = None
                    for station in self.stations:
                        if nextHopInterface == station.interface.name:
                            stationChosen = station
                    # TODO: validate station and socket
                    if is_socket_invalid(stationChosen.cliSock):
                        self.stations.remove(stationChosen)
                    else:
                        sendMac(nextHopIpaddress, stationChosen, ipPackObj)
                time.sleep(STATION_PQ_REFRESH_PERIOD)

    def serveUser(self):
        """
        read user input and execute commands
        """
        while not self.exitFlag:
            try: # select()
                inputReady, outputReady, exceptReady = select.select([sys.stdin], [], [], SELECT_TIMEOUT)
            except select.error as e:
                if not self.exitFlag:
                    print("error on select", e)
                return
            for sock in inputReady:
                if sock == sys.stdin:
                    # user input
                    uIn = sys.stdin.readline().strip()
                    self.processUserCommand(uIn)
                else:
                    print("Huh?")
                    pass

    def processUserCommand(self, uIn: str):
        """
        process user command for the station
        """
        sUIn = uIn.split()
        command = sUIn[0]
        if command.lower() == "quit":
            print("quitting station shutting down!")
            self.shutdown(True)
            sys.exit(0)
        elif command.lower() == "show":
            if len(sUIn) == 2:
                toShow = sUIn[1]
                if toShow.lower() == "arp":
                    for station in self.stations:
                        print(station.interface.name + ":-")
                        if station.arpCache.__len__() == 0:
                            print("nothing to show")
                        else:
                            print("\tIP\t\t: MAC")
                            for arpEntry in station.arpCache:
                                print("\t" + arpEntry + "\t: " + station.arpCache[arpEntry].mac)
                elif toShow.lower() == "pq":
                    for station in self.stations:
                        print(station.interface.name + ":-")
                        for msg in station.pendQ:
                            print(msg)
                elif toShow.lower() == "hosts":
                    print("Name\t: Ip")
                    for host in self.hosts:
                        print(host + "\t: " + self.hosts[host])
                elif toShow.lower() == "iface":
                    for station in self.stations:
                        print(station.interface)
                elif toShow.lower() == "rtable":
                    for route in self.rTable:
                        print(route)
                else:
                    print("unknown show command")
                    print("show usage :- \n\tshow arp\n\tshow pq\n\tshow hosts\n\tshow iface\n\tshow rtable")
            else:
                print("show usage :- \n\tshow arp\n\tshow pq\n\tshow hosts\n\tshow iface\n\tshow rtable")
        elif command.lower() == "send":
            self.send(uIn, sUIn)
        else:
            print("unknown command")
            print("usage :- \n\tquit\n\tshow arp\n\tshow pq\n\tshow hosts\n\tshow iface\n\tshow rtable\n\tsend <destination> <message>")

    def send(self, uIn, sUIn):
        """
        send message entered by user to its destination
        """
        # validate
        if len(sUIn) < 3:
            print("send usage:- send <destination> <message>")
            return

        """----------------IP----------------"""

        # get destination - whom should the message be sent
        destination = sUIn[1]
        destinationIp = ""
        # destinationMac = ""
        message = uIn[len(destination)+6:len(uIn)]
        pack = Packet(len(message), message)

        # check destination given is interface or ip
        if not isIp(destination):
            # if interface get ip from hosts - DNS Lookup
            for host in self.hosts:
                if destination.lower() == host.lower():
                    destinationIp = self.hosts[host]
            if destinationIp == "":
                # if we didn't find ip, give up
                print("DNS lookup failed - couldn't find ip address of " + destination + " in hostnames")
                return

        # figure out next hop ip address
        nextRoute = getNextRoute(self.rTable, destinationIp)
        nextHopIpaddress = nextRoute.nextHop
        nextHopInterface = nextRoute.ifaceName
        stationChosen = None
        for station in self.stations:
            if nextHopInterface == station.interface.name:
                stationChosen = station
        if stationChosen is None:
            print("error: unable to select a station to send packet")
            return

        # wrap message - ipPacket
        ipPack = IpPacket(destinationIp, stationChosen.interface.ip, 0, 0, pack.__dict__)

        """----------------MAC----------------"""

        sendMac(nextHopIpaddress, stationChosen, ipPack)

        """
        # check if we know the MAC address of nextHop ip address - arpCache
        if nextHopIpaddress == "0.0.0.0":
            nextHopIpaddress = destinationIp
        else:
            for station in self.stations:
                if station.arpCache.__contains__(nextHopIpaddress):
                    destinationMac = station.arpCache[nextHopIpaddress]

        # wrap message - ethernetPacket and put it in queue
        ethIpPack = EthernetPacket(destinationMac, stationChosen.interface.mac, "IP", ipPack.__dict__)
        stationChosen.pendQ.append(ethIpPack)

        if destinationMac == "":
            # send ARP req to bridge
            arpReq = ArpPacket(True, ipPack.srcIp, stationChosen.interface.mac, nextHopIpaddress, "")
            ethArpPack = EthernetPacket(destinationMac, stationChosen.interface.mac, "ARP", arpReq.__dict__)
            ethArpPackDict = ethArpPack.__dict__
            print(ethArpPackDict)
            data = json.dumps(ethArpPackDict)
            stationChosen.send(data)
        """

    def shutdown(self, sockShutdownFlag):
        """
        shutdown multi station
        """
        self.exitFlag = True
        for station in self.stations:
            station.shutdown(False, sockShutdownFlag)

def main():
    """
    Entry point
    """

    # check correct usage
    if len(sys.argv) != 5:
        print("usage:- python3 station.py -no/-route interface routing-table hostname")
        sys.exit(1)
    stationType = sys.argv[1]
    iFace = sys.argv[2]
    rTable = sys.argv[3]
    hosts = sys.argv[4]

    mStation = MultiStation(stationType, iFace, rTable, hosts)

    def sigHandler(sig, frame):
        print(" ctrl+c detected- station shutting down!")
        mStation.shutdown(True)
        sys.exit(0)

    # Handle SIGINT
    signal.signal(signal.SIGINT, sigHandler)

    # user input handling thread
    userThread = threading.Thread(target=MultiStation.serveUser, args=(mStation,))
    userThread.daemon = True
    userThread.start()
    mStation.start()

if __name__ == "__main__":
    main()
