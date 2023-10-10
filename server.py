# Names: Sai Jyothi Attuluri, Sai Nikhil Gummadavelli

# Server

import socket
import signal


class Server:
    """
    Server
    """

    def __init__(self, host, port):
        self.HOST = host
        self.PORT = port
        self.servSock = None

    def start(self):
        """
        Start server: Create a socket and start listening
        """
        self.servSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.servSock.bind((self.HOST, self.PORT))
        self.servSock.listen()
        return self.servSock

    def close(self):
        """
        close socket on exit
        """
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
