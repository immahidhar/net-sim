# Names: Sai Jyothi Attuluri, Sai Nikhil Gummadavelli

# Server

import sys
import socket
import select
import threading

from util import BUFFER_LEN, SELECT_TIMEOUT


class Server:
    """
    Server
    """

    def __init__(self, host, port):
        self.servSock = None
        self.HOST = host
        self.PORT = port
        self.threads = []
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
        print("server started: name = \"", socket.gethostname(), "\"", end =" ")
        # print("ip = \"", socket.gethostbyname_ex(socket.gethostname())[-1][0], "\"", end =" ")
        print("ip = \"", (self.servSock.getsockname())[0], "\"", end=" ")
        print("port = \"", self.servSock.getsockname()[1], "\"")
        return self.servSock

    def serve(self):
        """
        server connections
        :return:
        """
        while not self.exitFlag:
            try: # select()
                inputReady, outputReady, exceptReady = select.select([self.servSock], [], [], SELECT_TIMEOUT)
            except select.error as e:
                print("error on select", e)
                return

            for sock in inputReady:
                if sock == self.servSock:
                    # handle the server socket
                    self.acceptConnections()
                else:
                    print("Huh?")
                    pass

    def acceptConnections(self):
        """
        accept new connections
        :return:
        """
        # accept()
        clientSock, clientAddr = self.servSock.accept()
        print("new connection: ", clientSock)
        self.clientSocks.append(clientSock)
        clientReadThread = threading.Thread(target=self.readConnection, args=(clientSock,))
        self.threads.append(clientReadThread)
        clientReadThread.start()

    def readConnection(self, cliSock):
        """
        read data from connections
        :return:
        """
        while not self.exitFlag:
            # read from client socket
            try: # select()
                inputReady, outputReady, exceptReady = select.select([cliSock], [], [], SELECT_TIMEOUT)
            except select.error as e:
                print("error on select", e)
                return
            for sock in inputReady:
                if sock == cliSock:
                    try: # recv()
                        data = cliSock.recv(BUFFER_LEN)
                    except OSError as e:
                        if self.exitFlag:
                            return
                        print("recv error ", e)
                        self.clientSocks.remove(cliSock)
                        cliSock.close()
                        return
                    if not data:
                        if self.exitFlag:
                            return
                        print("client closed connection", cliSock)
                        self.clientSocks.remove(cliSock)
                        cliSock.close()
                        return
                    else:
                        self.processData(cliSock, data)
                else:
                    print("Huh?")
                    pass


    def processData(self, cliSock, data):
        """
        process data received
        :param cliSock:
        :param data:
        :return:
        """
        print(cliSock.getsockname(), " : ", data)

    def close(self):
        """
        close all sockets on exit
        """
        self.exitFlag = True
        for sock in self.clientSocks:
            print("closing client socket",  sock.getsockname())
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()
        print("closing server socket", self.servSock)
        self.servSock.close()

    def __str__(self):
        return self.servSock.getsockname()

    def __repr__(self):
        return self.servSock.getsockname()


def main():
    pass

if __name__ == "__main__":
    main()
