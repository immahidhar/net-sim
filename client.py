# Names: Sai Jyothi Attuluri, Sai Nikhil Gummadavelli

# Client

import sys
import socket
import select

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
        print("starting connection to",  self.server_addr)
        self.cliSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cliSock.connect(self.server_addr)
        print("connected to ", self.server_addr, " on ", self.cliSock.getsockname())

    def run(self):
        """
        run client - read from server
        :return:
        """
        print("client ready to read server data")
        while True:
            data = self.cliSock.recv(BUFFER_LEN)
            if not data:
                if self.exitFlag:
                    return
                print("server closed connection",  self.server_addr)
                return
            else:
                self.processData(self.cliSock, data)

    def runInput(self):
        """
        run input - read user input and send to server
        """
        print("client ready to take user input")
        while True:
            try:  # select()
                inputReady, outputReady, exceptReady = select.select([sys.stdin], [], [])
            except select.error as e:
                print("error on select", e)
                break
            for sock in inputReady:
                if sock == sys.stdin:
                    # user input
                    self.send(sys.stdin.readline())


    def processData(self, sock, data):
        """
        process data received
        :param sock:
        :param data:
        :return:
        """
        print(sock.getsockname(), " : ", data)

    def send(self, data):
        """
        send data to server
        """
        print("sending data to server:", data)
        self.cliSock.send(data)


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
