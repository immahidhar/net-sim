# Names: Sai Jyothi Attuluri, Sai Nikhil Gummadavelli

# Station

import sys
import select
import signal
import threading

import json

from client import Client
from dstruct import Interface, RoutingTable, IpPacket, ArpPacket, EthernetPacket, Packet
from util import SELECT_TIMEOUT, isIp, unpack, BUFFER_LEN, CLIENT_CONNECT_RETRIES


class Station(Client):
    """
    Station
    """

    def __init__(self, interface: Interface):
        self.exitFlag = False
        self.interface = interface
        self.addrFileName = "." + self.interface.lan + '.addr'
        self.portFileName = "." + self.interface.lan + '.port'
        self.bridgePort = None
        self.bridgeHost = None
        self.getBridgeAddr()
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
        self.validateBridgeAccept()
        clientThread = threading.Thread(target=Client.run, args=(self,))
        clientThread.start()
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
                    data = self.cliSock.recv(BUFFER_LEN)
                    if not data:
                        if self.exitFlag:
                            return False
                        print("server closed connection",  self.server_addr)
                        super().close(False)
                        return False
                    else:
                        data = str(data, 'UTF-8').strip()
                        if data == "accept":
                            print("bridge " + self.interface.lan + " accepted connection")
                            return True
                        elif data == "reject":
                            print("bridge " + self.interface.lan + " rejected connection")
                            return False
                        else:
                            print(data)
                else:
                    print("Huh?")
                    pass
            return False

    def processData(self, cliSock, dataBytes):
        """
        process data received
        :param cliSock:
        :param dataBytes:
        :return:
        """
        data = json.loads(str(dataBytes, 'UTF-8').strip())
        # must have received Ethernet packet - unpack it
        ethPack = unpack(EthernetPacket("", "", "", ""), data)
        print(cliSock.getpeername(), " : ", ethPack)
        packetType = ethPack.payload["type"]
        if packetType == ArpPacket.__name__:
            # process ARP packet received
            pass
        elif packetType == IpPacket.__name__:
            # process IP packet received
            pass

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
        self.arpCache = {} # arp cache - (ip: str, mac: str)
        self.pendQ = [] # pending queue
        self.hosts = {} # (iface, ip)
        self.rTable = []
        self.stations = []
        self.stationThreads = []
        self.loadInterface()
        self.loadHosts()
        self.loadRoutingTable()

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
                        station = Station(Interface(iface[0], iface[1], iface[2], iface[3], iface[4]))
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
                        self.rTable.append(RoutingTable(route[0], route[1], route[2], route[3]))
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

        for st in self.stationThreads:
            st.join()

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
                    for arpEntry in self.arpCache:
                        print(arpEntry + "\t: " + self.arpCache[arpEntry])
                elif toShow.lower() == "pq":
                    for msg in self.pendQ:
                        print(msg)
                elif toShow.lower() == "hosts":
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
        destinationMac = ""
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

        # wrap message - ipPacket
        ipPack = IpPacket(destinationIp, self.stations[0].interface.ip, 0, 0, pack.__dict__)

        """----------------MAC----------------"""

        # check if we know the MAC address of destination - arpCache
        for arpEntry in self.arpCache:
            if destinationIp == arpEntry:
                destinationMac = self.arpCache[arpEntry]

        if destinationMac == "":
            # if not, send ARP req to bridge and put it in queue
            # wrap message - ethernetPacket
            ethIpPack = EthernetPacket(destinationMac, self.stations[0].interface.mac, "IP", ipPack.__dict__)
            self.pendQ.append(ethIpPack)
            arpReq = ArpPacket(True, ipPack.srcIp, self.stations[0].interface.mac, destinationIp, "")
            ethArpPack = EthernetPacket(destinationMac, self.stations[0].interface.mac, "ARP", arpReq.__dict__)
            arpReqDict = ethArpPack.__dict__
            print(arpReqDict)
            data = json.dumps(arpReqDict)
            for station in self.stations:
                station.send(data)


        # if so, wrap it and send it


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
