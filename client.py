# Names: Sai Jyothi Attuluri, Sai Nikhil Gummadavelli

# Client

import socket
import threading

class Client:
    """
    Client
    """

    def __init__(self, host, port):
        self.HOST = host
        self.PORT = port
        self.servSock = None

    def connect(self):
        """
        connect to server
        :return:
        """
        server_addr = (self.HOST, self.PORT)
        print(f"Starting connection to {server_addr}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.connect_ex(server_addr)
