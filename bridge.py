# Names: Sai Jyothi Attuluri, Sai Nikhil Gummadavelli

# Bridge

import signal
import sys
import threading

from server import Server


class Bridge(Server):
    """
    Bridge
    """

    def __init__(self, host, port):
        super().__init__(host, port)
        serverThread = None

    def start(self):
        """
        Start bridge
        :return:
        """
        # start server
        super().start()
        serverThread = threading.Thread(target=super().serve(), args=())
        serverThread.start()
        serverThread.join()

    def shutdown(self):
        super().close()


def main():
    """
    Entry point
    """
    bridge = Bridge('', 0)

    def sigHandler(sig, frame):
        """
        Signal Handler to catch ctrl+c
        """
        print(" ctrl+c detected- bridge shutting down!")
        bridge.shutdown()
        sys.exit(0)

    # Handle SIGINT
    signal.signal(signal.SIGINT, sigHandler)
    print("signal Handler registered")

    # start bridge
    bridge.start()


if __name__ == "__main__":
    main()
