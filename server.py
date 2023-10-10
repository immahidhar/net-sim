# Names: Sai Jyothi Attuluri, Sai Nikhil Gummadavelli

# Server

import sys
import socket
import select
import threading

from util import BUFFER_LEN


class Server:
    """
    Server
    """

    def __init__(self, host, port):
        self.servSock = None
        self.HOST = host
        self.PORT = port
        self.clientSocks = []

    def start(self):
        """
        Start server: Create a socket and start listening
        """
        self.servSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.servSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.servSock.bind((self.HOST, self.PORT))
        self.servSock.listen()
        print("Server started:", self.servSock.getsockname())
        return self.servSock

    def serve(self):
        """
        server connections
        :return:
        """
        inSocks = [self.servSock, sys.stdin]
        flag = True
        while flag:
            try: # select()
                inputReady, outputReady, exceptReady = select.select(inSocks, [], [])
            except select.error as e:
                print("error on select", e)
                break

            for sock in inputReady:
                if sock == self.servSock:
                    # handle the server socket
                    self.acceptConnections()
                elif sock == sys.stdin:
                    # handle standard input
                    pass

    def acceptConnections(self):
        """
        accept new connections
        :return:
        """
        # accept()
        clientSock, clientAddr = self.servSock.accept()
        print(f"new connection: {clientSock} - {clientAddr}")
        self.clientSocks.append(clientSock)
        readThread = threading.Thread(target=self.readConnection, args=(clientSock,))
        readThread.start()

    def readConnection(self, sock: socket):
        """
        read data from connections
        :return:
        """
        while True:
            # read from client
            data = sock.recv(BUFFER_LEN)
            if not data:
                print(f'client connection closed {sock.getsockname()}')
                self.clientSocks.remove(sock)
                sock.close()
            else:
                self.processData(sock, data)

    def processData(self, sock, data):
        """
        process data received
        :param data:
        :return:
        """
        print(f"{sock.getsockname()}:{data}")

    def close(self):
        """
        close all sockets on exit
        """
        for sock in self.clientSocks:
            print(f"closing client socket {sock.getsockname()}")
            sock.close()
        print("Closing server socket", self.servSock)
        self.servSock.close()

    def __str__(self):
        return f'{self.servSock.getsockname()}'

    def __repr__(self):
        return f'{self.servSock.getsockname()}'


def main():
    pass


if __name__ == "__main__":
    main()
