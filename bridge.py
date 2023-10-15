# Names: Sai Jyothi Attuluri, Sai Nikhil Gummadavelli

# Bridge

import os
import sys
import time
import select
import signal
import socket
import threading

import json

from dstruct import EthernetPacket, ArpPacket, IpPacket, ClientDb
from server import Server
from util import SELECT_TIMEOUT, unpack, BRIDGE_SL_TIMEOUT, BRIDGE_SL_REFRESH_PERIOD, LOCAL_BROADCAST_MAC, \
    PACKET_END_CHAR, DEBUG, is_socket_invalid


class Bridge(Server):
    """
    Bridge
    """

    def __init__(self, host, port, lanName, numPorts):
        self.exitFlag = False
        super().__init__(host, port, numPorts)
        self.lanName = lanName
        self.numPorts = numPorts
        self.addrFileName = "." + self.lanName + '.addr'
        self.portFileName = "." + self.lanName + '.port'
        self.threads = []
        self.sLDb = {} # self learning port-mac database (mac: str, client: ClientDB)

    def start(self):
        """
        Start bridge
        :return:
        """
        super().start()
        self.saveBridgeAddr()
        # server Thread
        serverThread = threading.Thread(target=Server.serve, args=(self,))
        self.threads.append(serverThread)
        # self learning clean up thread
        slThread = threading.Thread(target=Bridge.cleanUpSLDb, args=(self,))
        slThread.daemon = True
        serverThread.start()
        slThread.start()
        print("bridge started")
        serverThread.join()

    def processData(self, cliSock, dataBytes):
        """
        process data received
        :param cliSock:
        :param dataBytes:
        :return:
        """
        dataStrList = str(dataBytes, 'UTF-8') #.strip()
        dataStrList = dataStrList.split(PACKET_END_CHAR)
        for dataStr in dataStrList:
            if dataStr == "":
                return
            if DEBUG:
                print(cliSock.getpeername(), " : ", dataStr)
            data = json.loads(dataStr)
            # must have received Ethernet packet - unpack it
            ethPack = unpack(EthernetPacket("", "", "", ""), data)
            # print(cliSock.getpeername(), " : ", ethPack)
            # update self learning database
            self.sLDb[ethPack.srcMac] = ClientDb(cliSock, time.time())
            packetType = ethPack.payload["type"]
            if packetType == ArpPacket.__name__:
                # process ARP packet received
                arpPack = ethPack.payload
                # check if ARP request or response
                if arpPack["req"] is True:
                    # broadcast to all clients
                    self.broadcastData(cliSock, dataStr, True)
                else:
                    # Get mac of destination station
                    destMac = arpPack["destMac"]
                    # check Db to fetch the respective client
                    if self.sLDb.__contains__(destMac) and not is_socket_invalid(self.sLDb[destMac].cliSock):
                        cliDb = self.sLDb[destMac]
                        # send over that client
                        self.sendData(cliDb.cliSock, dataStr)
                    else:
                        print("error: couldn't send packet, unknown mac", destMac)
            elif packetType == IpPacket.__name__:
                # process IP packet received
                ipPack = ethPack.payload
                # Get mac of destination
                destMac = ethPack.dstMac
                # check if broadcast mac
                if destMac == LOCAL_BROADCAST_MAC:
                    # broadcast to all clients except sender
                    self.broadcastData(cliSock, dataStr, False)
                    return
                # check Db to fetch the respective client
                if self.sLDb.__contains__(destMac) and not is_socket_invalid(self.sLDb[destMac].cliSock):
                    cliDb = self.sLDb[destMac]
                    # send over that client
                    if DEBUG:
                        print("passing to", cliDb.cliSock)
                    self.sendData(cliDb.cliSock, dataStr)
                else:
                    print("error: couldn't send packet, unknown mac", destMac)

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
        if uIn.lower() == "quit":
            print("quitting - bridge shutting down!")
            self.shutdown()
        elif uIn.lower() == "show sl":
            if self.sLDb.__len__() == 0:
                print("nothing to show")
                return
            print("MAC\t\t  : Station")
            for entry in self.sLDb:
                clientDb = self.sLDb[entry]
                if not is_socket_invalid(clientDb.cliSock):
                    print(entry + " : " + clientDb.cliSock.getpeername().__str__())
        else:
            print("unknown command")
            print("usage:-show sl\n\tquit")

    def cleanUpSLDb(self):
        """
        clean up self learning database once in a while:
        """
        while not self.exitFlag:
            rmEntries = []
            for entry in self.sLDb:
                client = self.sLDb[entry]
                currTime = time.time()
                oldTime = client.timestamp
                if currTime - oldTime >= BRIDGE_SL_TIMEOUT or is_socket_invalid(client.cliSock):
                    rmEntries.append(entry)
            for entry in rmEntries:
                self.sLDb.__delitem__(entry)
            time.sleep(BRIDGE_SL_REFRESH_PERIOD)

    def shutdown(self):
        # remove bridge address symbolic links
        self.exitFlag = True
        os.remove(self.addrFileName)
        os.remove(self.portFileName)
        # close server
        super().close()
        sys.exit(0)

    def saveBridgeAddr(self):
        with open(self.addrFileName, 'w') as addr:
            try:
                # TODO: change here
                # addr.write(socket.gethostbyname_ex(socket.gethostname())[-1][0])
                addr.write((self.servSock.getsockname())[0])
            except:
                print("error writing bridge ip address")
                self.shutdown()
        with open(self.portFileName, 'w') as port:
            try:
                port.write(str(self.servSock.getsockname()[1]))
            except:
                print("error writing bridge port")
                self.shutdown()

def bridgeLanExists(bridge: Bridge):
    """
    check if bridge address files with lanName already exists
    """
    try:
        with open(bridge.addrFileName, 'r') as addr:
            bridgeHost = addr.readline()
            if bridgeHost == "":
                return False
            else:
                return True
    except FileNotFoundError:
        return False

def main():
    """
    Entry point
    """

    # check correct usage
    if len(sys.argv) != 3:
        print("usage:- python3 bridge.py lan-name num-ports")
        sys.exit(1)
    lanName = sys.argv[1]
    numPorts = sys.argv[2]

    bridge = Bridge('', 0, lanName, numPorts)

    # validate lanName
    if bridgeLanExists(bridge):
        print("bridge with lan name", lanName, "already exists, provide another lan name")
        sys.exit(1)

    def sigHandler(sig, frame):
        """
        Signal Handler to catch ctrl+c
        """
        print(" ctrl+c detected- bridge shutting down!")
        bridge.shutdown()

    # Handle SIGINT
    signal.signal(signal.SIGINT, sigHandler)

    # user input handling thread
    userThread = threading.Thread(target=Bridge.serveUser, args=(bridge,))
    userThread.daemon = True
    userThread.start()
    # start bridge
    bridge.start()


if __name__ == "__main__":
    main()
