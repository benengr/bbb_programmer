import struct
from bootp.Utilities import _pack_ip
import random


class IpGenerator:
    def __init__(self, ip, netmask):
        self.server_ip = struct.unpack('!L', _pack_ip(ip))[0]
        self.netmask = struct.unpack('!L', _pack_ip(netmask))[0]
        self.anti_netmask = 0xFFFFFFFF - self.netmask

    def is_ip_valid(self, client_ip):
        # Exclude using the server's address, the network's address, the
        # broadcast address, and any IP already in use.
        if (client_ip == self.server_ip or
                (client_ip & self.netmask) == client_ip or
                (client_ip | self.netmask) == 0xFFFFFFFF):
            return False
        return True

    def generate_ip(self, bits):
        """
        Generates an IP from the provided 32 bits
        :param bits: 32-bit number.  In general, this is probably random
        :return: an IP address
        """
        return (self.server_ip & self.netmask) | (bits & self.anti_netmask)

    def generate_random_ip(self):
        return self.generate_ip(random.getrandbits(32))

