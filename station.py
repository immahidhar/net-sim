# Names: Sai Jyothi Attuluri, Sai Nikhil Gummadavelli

# Station

import sys
import signal
import threading

from client import Client

class Station:
    """
    Station
    """

    def __init__(self, lanName):
        self.lanName = lanName
        self.addrFileName = "." + self.lanName + '.addr'
        self.portFileName = "." + self.lanName + '.port'
        self.bridgePort = None
        self.bridgeHost = None
        self.getBridgeAddr()

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

def main():
    """
    Entry point
    """
    lanName = sys.argv[1]
    station = Station(lanName)
    client = Client(station.bridgeHost, station.bridgePort)
    def sigHandler(sig, frame):
        """
        Signal Handler to catch ctrl+c
        """
        print(" ctrl+c detected- station shutting down!")
        client.close(True)
        sys.exit(0)
    # Handle SIGINT
    signal.signal(signal.SIGINT, sigHandler)
    client.connect()
    clientThread = threading.Thread(target=client.run(), args=())
    clientThread.start()
    clientThread.join()


if __name__ == "__main__":
    main()
