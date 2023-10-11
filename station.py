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

    def __int__(self):
        pass

def main():
    client = Client(sys.argv[1], int(sys.argv[2]))
    def sigHandler(sig, frame):
        """
        Signal Handler to catch ctrl+c
        """
        print(" ctrl+c detected- bridge shutting down!")
        client.close()
        sys.exit(0)
    # Handle SIGINT
    signal.signal(signal.SIGINT, sigHandler)
    print("signal Handler registered")
    client.connect()
    clientThread = threading.Thread(target=client.run(), args=())
    clientThread.start()
    clientThread.join()


if __name__ == "__main__":
    main()
