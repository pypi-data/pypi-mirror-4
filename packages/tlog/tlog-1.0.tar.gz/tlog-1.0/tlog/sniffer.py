import socket

class Sniffer(object):
    ETH_P_ALL = 3
    
    def __init__(self, interface, snap=1500):
        self.interface = interface
        self.socket = socket.socket ( socket.PF_PACKET, socket.SOCK_RAW, socket.htons(self.ETH_P_ALL) )
        self.socket.bind ( (self.interface, self.ETH_P_ALL) )
        self.count = 0
        self.snap = snap
        
    def next(self):
        packet_buffer = self.socket.recv(self.snap)
        self.count += 1
        return packet_buffer

    def close(self):
        self.socket.close()
