# Names: Sai Jyothi Attuluri, Sai Nikhil Gummadavelli

# Client

import sys
import socket
import select

from util import BUFFER_LEN, SELECT_TIMEOUT


class Client:
    """
    Client
    """

    def __init__(self, host, port):
        self.HOST = host
        self.PORT = port
        self.server_addr = (self.HOST, self.PORT)
        self.cliSock = None
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
        while not self.exitFlag:
            try: # select()
                inputReady, outputReady, exceptReady = select.select([self.cliSock], [], [], SELECT_TIMEOUT)
            except select.error as e:
                print("error on select", e)
                return
            for sock in inputReady:
                if sock == self.cliSock:
                    data = self.cliSock.recv(BUFFER_LEN)
                    if not data:
                        if self.exitFlag:
                            return
                        print("server closed connection",  self.server_addr)
                        self.close(False)
                        return
                    else:
                        self.processData(self.cliSock, data)
                else:
                    print("Huh?")
                    pass

    def runInput(self):
        """
        run input - read user input and send to server
        """
        print("client ready to take user input")
        while not self.exitFlag:
            try:  # select()
                inputReady, outputReady, exceptReady = select.select([sys.stdin], [], [], SELECT_TIMEOUT)
            except select.error as e:
                print("error on select", e)
                break
            for sock in inputReady:
                if sock == sys.stdin:
                    # user input
                    self.send(sys.stdin.readline())
        print("client done taking user input")


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


    def close(self, shutdownFlag):
        """
        close sockets
        :return:
        """
        self.exitFlag = True
        print("closing client socket", self.cliSock)
        if shutdownFlag:
            self.cliSock.shutdown(socket.SHUT_RDWR)
        self.cliSock.close()

    def __str__(self):
        return self.cliSock.getsockname()

    def __repr__(self):
        return self.cliSock.getsockname()


def main():
    pass

if __name__ == "__main__":
    main()
