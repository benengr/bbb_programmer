import socket
import struct
import sys


def _pack_ip(ip_addr):
    """Pack a dotted quad IP string into a 4 byte string."""
    return socket.inet_aton(ip_addr)


def _unpack_ip(ip_addr):
    """Unpack a 4 byte IP address into a dotted quad string."""
    return socket.inet_ntoa(ip_addr)


def _pack_mac(mac_addr):
    """Pack a MAC address (00:00:00:00:00:00) into a 6 byte string."""
    fields = [int(x, 16) for x in mac_addr.split(':')]
    return struct.pack('!6B', *fields)


def compute_checksum(message):
    """Calculates the 16-bit one's complement of the one's complement sum
    of a given message."""

    # If the message length isn't a multiple of 2 bytes, we pad with
    # zeros
    if len(message) % 2:
        message += struct.pack('x')

    # We build our blocks to sum
    to_sum = struct.unpack('!%dH' % (len(message) / 2), message)

    # UDP checksum
    checksum = 0
    for v in to_sum:
        checksum += v
        if checksum > 2 ** 16:
            checksum = (checksum & 0xFFFF) + 1
    return 0xFFFF - checksum


def get_ip_config_for_iface(iface):
    """Retrieve and return the IP address/netmask and MAC address of the
    given interface."""

    if 'linux' not in sys.platform:
        raise NotImplementedError("get_ip_address_for_iface is not "
                                  "implemented on your OS.")

    def ip_from_response(resp):
        return socket.inet_ntoa(resp[20:24])

    def mac_from_response(resp):
        _mac = struct.unpack('!6B', resp[18:24])
        return ':'.join(['%02x' % x for x in _mac])

    import fcntl
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ifname = struct.pack('256s', bytes(iface[:15], 'utf-8'))
    ip = fcntl.ioctl(s.fileno(), SIOCGIFADDR, ifname)
    mask = fcntl.ioctl(s.fileno(), SIOCGIFNETMASK, ifname)
    mac = fcntl.ioctl(s.fileno(), SIOCGIFHWADDR, ifname)
    return ip_from_response(ip), ip_from_response(mask), \
        mac_from_response(mac)


SIOCGIFADDR = 0x8915  # IP address for interface
SIOCGIFNETMASK = 0x891B  # Netmask for interface
SIOCGIFHWADDR = 0x8927  # MAC address for interface