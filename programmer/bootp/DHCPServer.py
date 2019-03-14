import struct
import socket
import sys
import logging
import random
from bootp import Constants
import time
from bootp.DHCPPacket import DhcpPacket, NotDhcpPacketError

# Linux ioctl() commands to query the kernel.
SIOCGIFADDR = 0x8915  # IP address for interface
SIOCGIFNETMASK = 0x891B  # Netmask for interface
SIOCGIFHWADDR = 0x8927  # MAC address for interface
log = logging.getLogger('dhcpd')

# DHCP lease timeout in seconds. Internally, we wait longer, to let
# the client wrap up cleanly.
DHCP_LEASE_TIMEOUT = 10 * 60  # 10 minutes
DHCP_LEASE_TIMEOUT_INTERNAL = 15 * 60  # 15 minutes


class UninterestingBootpPacket(Exception):
    """Packet is BOOTP, but we just don't care about it."""


class BootpServerConfigurationError(Exception):
    """The configuration of the pTFTPd is incorrect."""
    pass


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


class DHCPServer(object):
    def __init__(self, interface, bootfile, router=None, tftp_server=None):
        self.interface = interface
        self.ip, self.netmask, self.mac = get_ip_config_for_iface(interface)
        self.hostname = socket.gethostname()
        self.bootfile = bootfile
        self.router = router or self.ip
        self.tftp_server = tftp_server or self.ip
        self.ips_allocated = {}
        self.name_servers = None

        self.sock = socket.socket(socket.PF_PACKET, socket.SOCK_RAW)
        self.sock.bind((self.interface, Constants.ETHERNET_IP_PROTO))

    def serve_forever(self):
        log.info('Serving BOOTP requests on %s' % self.interface)
        while True:
            data = self.sock.recv(4096)
            try:
                pkt = DhcpPacket(data)
                log.info("Receipt DHCP request from: %s", pkt.vendor_class)
                self.handle_bootp_request(pkt)
                log.debug("Boot request handled")

            except (NotDhcpPacketError, UninterestingBootpPacket):
                continue

    def handle_bootp_request(self, pkt):
        # Clean up old leases before trying to get one for our new
        # client.
        self.gc_allocated_ips()
        ip = ''
        if pkt.op == Constants.DHCP_OP_DHCPDISCOVER:
            ip = self.generate_free_ip()
            log.info('Offering to boot client %s (uuid : %s)' % (ip, pkt.uuid))
        elif pkt.op == Constants.DHCP_OP_DHCPREQUEST:
            timeout = time.time() + DHCP_LEASE_TIMEOUT_INTERNAL
            if (pkt.requested_ip and
                    pkt.requested_ip not in self.ips_allocated):
                self.ips_allocated[pkt.requested_ip] = timeout
                ip = pkt.requested_ip
            else:
                ip = self.generate_free_ip()
                self.ips_allocated[ip] = timeout
            log.info('PXE booting client %s (uuid : %s)' % (ip, pkt.uuid))

        filename = DHCPServer.get_filename(pkt.vendor_class)
        self.sock.send(self.encode_dhcp_reply(pkt, ip, filename))

    def gc_allocated_ips(self):
        current = time.time()
        old = [ip for ip, to in self.ips_allocated.items()
               if to <= current]
        for ip in old:
            log.info('Lease on %s expired' % ip)
            del self.ips_allocated[ip]

    @staticmethod
    def get_filename(vendor_class):
        if vendor_class == "AM335x ROM":
            return "u-boot-spl-restore.bin"
        elif vendor_class == "AM335x U-Boot SPL":
            return 'u-boot-restore.img'
        else:
            return 'zImage'

    def encode_dhcp_reply(self, request_pkt, client_ip, filename):
        return DHCPServer._encode_dhcp_reply(request_pkt, client_ip, filename,
                                             self.mac, self.ip, self.netmask,
                                             self.tftp_server, self.router,
                                             self.name_servers)

    @staticmethod
    def _encode_dhcp_reply(request_pkt, client_ip, filename,
                           mac, ip, netmask,
                           tftp_server, router, name_servers):
        # Basic DHCP reply
        reply = struct.pack('!B'  # The op (0x2)
                            'B'  # The htype (Ethernet -> 0x1)
                            'B'  # The hlen (0x6)
                            'x'  # The hops field, useless
                            'L'  # XID
                            '8x'  # Useless fields
                            '4s'  # Client IP address
                            '4s'  # Next server IP address (TFTP server)
                            '4x'  # Useless fields
                            '6s'  # Client MAC address
                            '74x'  # BOOTP legacy padding.
                            '128s'  # PXE boot file
                            'L',  # Magic cookie
                            0x2, 0x1, 0x6, request_pkt.xid,
                            _pack_ip(client_ip), _pack_ip(tftp_server),
                            request_pkt.client_mac,
                            bytes(filename, 'utf-8'), Constants.DHCP_MAGIC_COOKIE)

        # DHCP options relevant to PXE
        reply_kind = {
            Constants.DHCP_OP_DHCPDISCOVER: Constants.DHCP_OP_DHCPOFFER,
            Constants.DHCP_OP_DHCPREQUEST: Constants.DHCP_OP_DHCPACK
        }[request_pkt.op]
        dhcp_options = [
            (Constants.DHCP_OPTION_OP, bytes([reply_kind])),
            (Constants.DHCP_OPTION_LEASE_TIME, struct.pack('!L', DHCP_LEASE_TIMEOUT)),
            (Constants.DHCP_OPTION_SUBNET, _pack_ip(netmask)),
            (Constants.DHCP_OPTION_ROUTER, _pack_ip(router)),
            (Constants.DHCP_OPTION_SERVER_ID, _pack_ip(ip)),
        ]

        if name_servers:
            dns_servers = ''
            for name_server in name_servers:
                dns_servers += _pack_ip(name_server)
            dhcp_options.append((Constants.DHCP_OPTION_DNS, dns_servers))

        buf = []
        for code, data in dhcp_options:
            buf.append(struct.pack('!BB', code, len(data)))
            buf.append(data)
        reply += b''.join(buf)
        reply += bytes([0xFF])

        # Construct the UDP datagram. We don't checksum, for
        # simplicity. UDP conformant clients should not care anyway, we
        # set the field to the "checksum not computed" value.
        reply = struct.pack('!HHH2x', 67, 68, len(reply) + 8) + reply

        # Now the IP datagram...
        ip_header1 = struct.pack('!BxH4xBB', 0x45, 20 + len(reply), 0xFF,
                                 Constants.IP_UDP_PROTO)
        ip_header2 = struct.pack('4s4s', _pack_ip(ip),
                                 _pack_ip('255.255.255.255'))
        # Header checksum computation
        checksum = 0
        for v in struct.unpack('!5H', ip_header1) + \
                struct.unpack('!4H', ip_header2):
            checksum += v
            if checksum > 2 ** 16:
                checksum = (checksum & 0xFFFF) + 1
        checksum = 0xFFFF - checksum
        reply = ip_header1 + struct.pack('!H', checksum) + ip_header2 + reply

        # And finally the ethernet frame.
        reply = struct.pack('!6s6sH', _pack_mac('ff:ff:ff:ff:ff:ff'),
                            _pack_mac(mac),
                            Constants.ETHERNET_IP_PROTO) + reply

        # Bingo, one DHCP reply russian doll^W^Wpacket!
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
