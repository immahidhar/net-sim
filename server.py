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
        self.exitFlag = False

    def start(self):
        """
        Start server: Create a socket and start listening
        """
        self.servSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.servSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.servSock.bind((self.HOST, self.PORT))
        self.servSock.listen()
        print(f"server started: name\"{socket.gethostname()}\" "
              f"ip\"{socket.gethostbyname_ex(socket.gethostname())[-1]}\" "
              f"port\"{ self.servSock.getsockname()[1]}\"")
        return self.servSock

    def serve(self):
        """
        server connections
        :return:
        """
        inSocks = [self.servSock, sys.stdin]
        while True:
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

    def readConnection(self, cliSock: socket):
        """
        read data from connections
        :return:
        """
        while True:
            # read from client socket
            try:
                data = cliSock.recv(BUFFER_LEN)
            except OSError as e:
                if self.exitFlag:
                    return
                print(f"recv error {e}")
                self.clientSocks.remove(cliSock)
                cliSock.close()
                return
            if not data:
                if self.exitFlag:
                    return
                print(f'client closed connection{cliSock}')
                self.clientSocks.remove(cliSock)
                cliSock.close()
                return
            else:
                self.processData(cliSock, data)

    def processData(self, cliSock, data):
        """
        process data received
        :param cliSock:
        :param data:
        :return:
        """
        print(f"{cliSock.getsockname()} : {data}")

    def close(self):
        """
        close all sockets on exit
        """
        self.exitFlag = True
        for sock in self.clientSocks:
            print(f"closing client socket {sock.getsockname()}")
            sock.close()
        print("closing server socket", self.servSock)
        self.servSock.close()

    def __str__(self):
        return f'{self.servSock.getsockname()}'

    def __repr__(self):
        return f'{self.servSock.getsockname()}'


def main():
    pass

if __name__ == "__main__":
    main()
