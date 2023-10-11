# Names: Sai Jyothi Attuluri, Sai Nikhil Gummadavelli

# Client

import socket

from util import BUFFER_LEN


class Client:
    """
    Client
    """

    def __init__(self, host, port):
        self.HOST = host
        self.PORT = port
        self.server_addr = (self.HOST, self.PORT)
        self.cliSock = None
        self.servSocks = []
        self.exitFlag = False

    def connect(self):
        """
        connect to server
        :return:
        """
        print(f"starting connection to {self.server_addr}")
        self.cliSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # clearself.cliSock.setblocking(False)
        self.cliSock.connect(self.server_addr)
        print(f"connected to {self.server_addr} on {self.cliSock.getsockname()}")

    def run(self):
        """
        run client
        :return:
        """
        while True:
            data = self.cliSock.recv(BUFFER_LEN)
            if not data:
                if self.exitFlag:
                    return
                print(f'server closed connection {self.server_addr}')
                return
            else:
                self.processData(self.cliSock, data)

    def processData(self, sock, data):
        """
        process data received
        :param sock:
        :param data:
        :return:
        """
        print(f"{sock.getsockname()}:{data}")


    def close(self):
        """
        close sockets
        :return:
        """
        self.exitFlag = True
        print("closing client socket", self.cliSock)
        self.cliSock.close()


def main():
    pass

if __name__ == "__main__":
    main()
