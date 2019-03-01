import struct
import socket
import sys
import logging
import random
from bootp import Constants
from bootp.BootpPacket import BootpPacket, NotBootpPacketError

# Linux ioctl() commands to query the kernel.
SIOCGIFADDR = 0x8915                  # IP address for interface
SIOCGIFNETMASK = 0x891B               # Netmask for interface
SIOCGIFHWADDR = 0x8927                # MAC address for interface
logger = logging.getLogger('bootpd')


class UninterestingBootpPacket(Exception):
    """Packet is BOOTP, but we just don't care about it."""


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
        mac = struct.unpack('!6B', resp[18:24])
        return ':'.join(['%02x' % x for x in mac])

    import fcntl
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ifname = struct.pack('256s', iface[:15])
    ip = fcntl.ioctl(s.fileno(), SIOCGIFADDR, ifname)
    mask = fcntl.ioctl(s.fileno(), SIOCGIFNETMASK, ifname)
    mac = fcntl.ioctl(s.fileno(), SIOCGIFHWADDR, ifname)
    return ip_from_response(ip), ip_from_response(mask), \
        mac_from_response(mac)


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


class BOOTPServer(object):
    def __init__(self, interface, bootfile, router=None, tftp_server=None):
        self.interface = interface
        self.ip, self.netmask, self.mac = get_ip_config_for_iface(interface)
        self.hostname = socket.gethostname()
        self.bootfile = bootfile
        self.router = router or self.ip
        self.tftp_server = tftp_server or self.ip
        self.ips_allocated = {}

        self.sock = socket.socket(socket.PF_PACKET, socket.SOCK_RAW)
        self.sock.bind((self.interface, Constants.ETHERNET_IP_PROTO))

    def serve_forever(self):
        logger.info('Serving BOOTP requests on %s' % self.interface)
        while True:
            data = self.sock.recv(4096)
            try:
                pkt = BootpPacket(data)
                logger.info("Receipt bootp request from: %s", pkt.vendor_class)
                self.handle_bootp_request(pkt)

            except (NotBootpPacketError, UninterestingBootpPacket):
                continue

    def handle_bootp_request(self, pkt):
        # If the server is explicitly requested, and it's not ours,
        # we just ignore it
        if pkt.sname and pkt.sname != self.hostname:
            raise UninterestingBootpPacket()

        ip = self.generate_free_ip()
        filename = self.get_filename(pkt.vendor_class)
        logger.info('Offering to boot client %s' % ip)
        logger.info('Booting client %s with file %s' % (ip, filename))

        self.sock.send(self.encode_bootp_reply(pkt, ip, filename))

    def get_filename(self, vendor_class):
        if vendor_class == "AM335x ROM":
            return "spl_image"
        elif vendor_class == "AM33":
            return 'uboot_image'
        else:
            return 'default_image'

    def encode_bootp_reply(self, request_pkt, client_ip, filename):
        # Basic BOOTP reply
        reply = struct.pack('!B'    # The op (0x2)
                            'B'     # The htype (Ethernet -> 0x1)
                            'B'     # The hlen (0x6)
                            'x'     # The hops field, useless
                            'L'     # XID
                            '2x'    # secs since boot, useless for the server
                            'H'     # bootp flags (Broadcast -> 0x8000)
                            '4x'    # ciaddr, useless for the server
                            '4s'    # Client IP address
                            '4s'    # Next server IP address (TFTP server)
                            '4x'    # Gateway IP Adress, useless
                            '6s'    # Client MAC address
                            '10x'   # End of MAC Address
                            '64s'   # Server host name, often useless
                            '128s'  # PXE boot file
                            'L',    # Magic cookie
                            0x2, 0x1, 0x6, request_pkt.xid, 0x8000,
                            _pack_ip(client_ip), _pack_ip(self.tftp_server),
                            request_pkt.client_mac, self.hostname,
                            filename, Constants.BOOTP_MAGIC_COOKIE)

        bootp_options = (
            (Constants.BOOTP_OPTION_SUBNET, _pack_ip(self.netmask)),
            (Constants.BOOTP_OPTION_GATEWAY, _pack_ip(self.router)),
            )

        options = ''
        for option, data in bootp_options:
            options += struct.pack('!BB', option, len(data))
            options += data
        reply += options + str(struct.pack('!B', 0xff))

        # We add the padding bytes to fit the full size of a BOOTP packet
        if len(reply) < Constants.BOOTP_PACKET_SIZE:
            reply += struct.pack(str(Constants.BOOTP_PACKET_SIZE - len(reply)) + 'x')

        # Construct the UDP datagram.
        # First, the checksum. Here we build our pseudo IP headers required
        # for the checksum, and then compute the checksum.
        udp_headers = struct.pack('!HHH', 67, 68, len(reply) + 8)
        pseudo_header = struct.pack('!4s4sxBH', _pack_ip(self.ip),
                                    _pack_ip('255.255.255.255'), Constants.IP_UDP_PROTO,
                                    len(udp_headers) + 2 + len(reply))

        pseudo_packet = pseudo_header + udp_headers + reply
        checksum = compute_checksum(pseudo_packet)

        reply = udp_headers + struct.pack('!H', checksum) + reply

        # Now the IP datagram...
        ip_header1 = struct.pack('!BxH4xBB', 0x45, 20+len(reply), 0xFF,
                                 Constants.IP_UDP_PROTO)
        ip_header2 = struct.pack('4s4s', _pack_ip(self.ip),
                                 _pack_ip('255.255.255.255'))
        checksum = compute_checksum(ip_header1 + ip_header2)

        reply = ip_header1 + struct.pack('!H', checksum) + ip_header2 + reply

        # And finally the ethernet frame.
        reply = struct.pack('!6s6sH', _pack_mac('ff:ff:ff:ff:ff:ff'),
                            _pack_mac(self.mac),
                            Constants.ETHERNET_IP_PROTO) + reply

        # And here is our BOOTP packet
        return reply

    def generate_free_ip(self):
        server_ip = struct.unpack('!L', _pack_ip(self.ip))[0]
        netmask = struct.unpack('!L', _pack_ip(self.netmask))[0]
        anti_netmask = 0xFFFFFFFF - netmask

        while True:
            entropy = random.getrandbits(32)

            client_ip = (server_ip & netmask) | (entropy & anti_netmask)

            # Exclude using the server's address, the network's address, the
            # broadcast address, and any IP already in use.
            if (client_ip == server_ip or
                    (client_ip & netmask) == 0 or
                    (client_ip | netmask) == 0xFFFFFFFF):
                continue

            ip = _unpack_ip(struct.pack('!L', client_ip))
            if ip in self.ips_allocated:
                continue

            return ip
