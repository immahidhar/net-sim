# Names: Sai Jyothi Attuluri, Sai Nikhil Gummadavelli

# Bridge

import os
import sys
import select
import signal
import socket
import threading

from server import Server
from util import SELECT_TIMEOUT


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
        self.serverThread = None

    def start(self):
        """
        Start bridge
        :return:
        """
        super().start()
        self.saveBridgeAddr()
        self.serverThread = threading.Thread(target=Server.serve, args=(self,))
        self.threads.append(self.serverThread)
        print("bridge started")
        self.serverThread.start()
        self.serverThread.join()

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
            print("quitting - station shutting down!")
            self.shutdown()
        elif uIn.lower() == "show sl":
            pass
        else:
            print("unknown command")
            print("usage:-show sl\n\tquit")

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
