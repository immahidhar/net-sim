# Names: Sai Jyothi Attuluri, Sai Nikhil Gummadavelli

# Station

import sys
import select
import signal
import threading

from client import Client
from util import SELECT_TIMEOUT


class Station(Client):
    """
    Station
    """

    def __init__(self, name, ip, snMask, mac, lanName):
        self.exitFlag = False
        self.name = name
        self.ip = ip
        self.snMask = snMask
        self.mac = mac
        self.lanName = lanName
        self.addrFileName = "." + self.lanName + '.addr'
        self.portFileName = "." + self.lanName + '.port'
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
            print("no bridge with lan name", self.lanName, "found")
            sys.exit(1)

    def start(self):
        """
        start station
        """
        super().connect()
        clientThread = threading.Thread(target=Client.run, args=(self,))
        clientThread.start()
        clientThread.join()

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

    def __init__(self, stationType, iFace, rTable, hosts):
        self.exitFlag = False
        self.numStations = 0
        self.stationType = stationType
        self.iFaceFileName = iFace
        self.rTableFileName = rTable
        self.hostsFileName = hosts
        self.hosts = {}
        self.routes = {}
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
                        station = Station(iface[0], iface[1], iface[2], iface[3], iface[4])
                        self.stations.append(station)
                        self.numStations = self.numStations + 1
                except:
                    print("error reading interface file")
                    sys.exit(1)
        except FileNotFoundError as e:
            print(e)
            sys.exit(1)
        print("interface loaded")

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
        print("hosts loaded")

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
                        self.routes[route[0]] = [route[1], route[2], route[3]]
                except:
                    print("error reading hosts file")
                    sys.exit(1)
        except FileNotFoundError as e:
            print(e)
            sys.exit(1)
        print("routing table loaded")
        print(self.routes)

    def start(self):
        """
        start multi station
        """
        # start stations
        for station in self.stations:
            stationThread = threading.Thread(target=Station.start, args=(station,))
            self.stationThreads.append(stationThread)
            stationThread.daemon = True
            stationThread.start()
        print("station started")

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
                    pass
                elif toShow.lower() == "pq":
                    pass
                elif toShow.lower() == "hosts":
                    print(self.hosts)
                elif toShow.lower() == "iface":
                    for station in self.stations:
                        print(station.name)
                elif toShow.lower() == "rtable":
                    print(self.routes)
                else:
                    print("unknown show command")
                    print("show usage :- \n\tshow arp\n\tshow pq\n\tshow hosts\n\tshow iface\n\tshow rtable")
            else:
                print("show usage :- \n\tshow arp\n\tshow pq\n\tshow hosts\n\tshow iface\n\tshow rtable")
        elif command.lower() == "send":
            pass
        else:
            print("unknown command")
            print("usage :- \n\tquit\n\tshow arp\n\tshow pq\n\tshow hosts\n\tshow iface\n\tshow rtable\n\tsend <destination> <message>")

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
        print("usage:- python3 station.py -no/-route interface routingtable hostname")
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
