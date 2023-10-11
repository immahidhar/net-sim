# Names: Sai Jyothi Attuluri, Sai Nikhil Gummadavelli

# Bridge

import signal
import socket
import sys
import threading

from server import Server


class Bridge(Server):
    """
    Bridge
    """

    def __init__(self, host, port, lanName):
        super().__init__(host, port)
        self.lanName = lanName
        self.addrFileName = "." + self.lanName + '.addr'
        self.portFileName = "." + self.lanName + '.port'
        self.serverThread = None

    def start(self):
        """
        Start bridge
        :return:
        """
        # start server
        super().start()
        self.saveBridgeAddr()
        self.serverThread = threading.Thread(target=super().serve(), args=())
        self.serverThread.start()
        self.serverThread.join()

    def shutdown(self):
        super().close()
        sys.exit(0)

    def saveBridgeAddr(self):
        with open(self.addrFileName, 'w') as addr:
            try:
                addr.write(socket.gethostbyname_ex(socket.gethostname())[-1][0])
            except:
                print("error writing bridge ip address")
                self.shutdown()
        with open(self.portFileName, 'w') as port:
            try:
                port.write(str(self.servSock.getsockname()[1]))
            except:
                print("error writing bridge port")
                self.shutdown()


def main():
    """
    Entry point
    """
    lanName = sys.argv[1]
    bridge = Bridge('', 0, lanName)

    def sigHandler(sig, frame):
        """
        Signal Handler to catch ctrl+c
        """
        print(" ctrl+c detected- bridge shutting down!")
        bridge.shutdown()

    # Handle SIGINT
    signal.signal(signal.SIGINT, sigHandler)

    # start bridge
    bridge.start()


if __name__ == "__main__":
    main()
