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
        while not self.exitFlag:
            try: # select()
                inputReady, outputReady, exceptReady = select.select([self.cliSock, sys.stdin], [], [], SELECT_TIMEOUT)
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
                elif sock == sys.stdin:
                    # user input
                    data = sys.stdin.readline()
                    self.send(data)
                else:
                    print("Huh?")
                    pass

    def processData(self, sock, data):
        """
        process data received
        :param sock:
        :param data:
        :return:
        """
        print(sock.getpeername(), " : ", str(data, 'UTF-8').strip())

    def send(self, data: str):
        """
        send data to server
        """
        self.cliSock.send(bytes(data, 'utf-8'))


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
