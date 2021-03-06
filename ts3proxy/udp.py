import time
import socket
import select

from .ts3client import Ts3Client

"""udp relay class

class for relaying the teamspeak3 udp communication stuff
"""


class Udp():

    def __init__(self, relayPort, remoteAddr, remotePort):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(("0.0.0.0", relayPort))
        self.remoteAddr = remoteAddr
        self.remotePort = remotePort
        self.clients = {}

    def relay(self):
        while True:
            readable, writable, exceptional = select.select(list(self.clients.values()) + [self.socket], [], [], 1)
            for s in readable:
                # if ts3 server answers to a client
                if isinstance(s, Ts3Client):
                    data, addr = s.socket.recvfrom(1024)
                    self.socket.sendto(data, s.addr)
                else:
                    # if a client sends something to a ts3 server
                    data, addr = s.recvfrom(1024)
                    # if its a new and unkown client
                    if addr not in self.clients:
                        print('connected:', addr)
                        self.clients[addr] = Ts3Client(socket.socket(socket.AF_INET, socket.SOCK_DGRAM), addr)
                    # send data to ts3 server
                    self.clients[addr].socket.sendto(data, (self.remoteAddr, self.remotePort))
            # close sockets of disconnected clients
            for addr, client in list(self.clients.items()):
                if client.last_seen <= time.time() - 2:
                    try:
                        client.socket.close()
                    except:
                        pass
                    print('disconnected:', addr)
                    del self.clients[addr]
