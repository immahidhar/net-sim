# Names: Sai Jyothi Attuluri, Sai Nikhil Gummadavelli

# Bridge

import signal
import sys

from server import Server


class Bridge(Server):
    """
    Bridge
    """

    def __init__(self, host, port):
        super().__init__(host, port)

    def start(self):
        """
        Start bridge
        :return:
        """
        super().start()

    def shutdown(self):
        super().close()


def main():
    """
    Entry point
    """
    bridge = Bridge("127.0.0.1", 0)
    bridge.start()

    def sigHandler(sig, frame):
        """
        Signal Handler to catch ctrl+c
        """
        print("Ctrl+C detected. Bridge shutting down!")
        bridge.shutdown()
        sys.exit(0)

    # Handle SIGINT
    signal.signal(signal.SIGINT, sigHandler)

    print("Server started:", bridge.servSock.getsockname())

    bridge.shutdown()


if __name__ == "__main__":
    main()
