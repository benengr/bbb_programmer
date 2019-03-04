import struct
import bootp.Constants as Constants
import socket


class NotDhcpPacketError(Exception):
    def __init__(self, message):
        self.message = message
    """Packet being decoded is not a DHCP packet."""


class UninterestingDhcpPacket(Exception):
    """Packet is DHCP, but not of interest to us."""


# Client UUID length. Some PXE clients use UUID2 to provide the client machine
# MAC address, resulting in invalid UUID parsing. We ensure we're dealing with
# client UUID by checking their length (16 bytes).
DHCP_CLIENT_UUID_LENGTH = 16


def _dhcp_options(options):
    """Generate a sequence of DHCP options from a raw byte stream."""
    i = 0
    while i < len(options):
        code = options[i]

        # Handle pad and end options.
        if code == 0:
            i += 1
            continue
        if code == 255:
            return

        # Extract and yield the option number and option value.
        data_len = options[i+1]
        data = options[i + 2:i + 2 + data_len]
        i += 2 + data_len
        yield (code, data)


def _unpack_uuid(uuid):
    """Unpack a PXE UUID to its long form
    (xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)."""
    fields = ['%02x' % x for x in struct.unpack('!16B', uuid)]
    return '%s-%s-%s-%s-%s' % (''.join(fields[:4]),
                               ''.join(fields[4:6]),
                               ''.join(fields[6:8]),
                               ''.join(fields[8:10]),
                               ''.join(fields[10:16]))


def _unpack_ip(ip_addr):
    """Unpack a 4 byte IP address into a dotted quad string."""
    return socket.inet_ntoa(ip_addr)


class DhcpPacket(object):
    def __init__(self, pkt):
        # Check the ethernet type. It needs to be IP (0x800).
        if struct.unpack('!H', pkt[12:14])[0] != Constants.ETHERNET_IP_PROTO:
            raise NotDhcpPacketError("Invalid Ethernet Protocol")
        self.server_mac, self.client_mac = pkt[0:6], pkt[6:12]

        # Strip off the ethernet frame and check the IP packet type. It should
        # be UDP (0x11)
        pkt = pkt[14:]
        if pkt[9] != Constants.IP_UDP_PROTO:
            raise NotDhcpPacketError("Not UDP Protocol")

        # Strip off the IP header and check the source/destination ports in the
        # UDP datagram. The packet should be from port 68 to port 67 to
        # tentatively be DHCP.
        header_len = (pkt[0] & 0xF) * 4
        pkt = pkt[header_len:]
        (src, dst) = struct.unpack('!2H', pkt[:4])
        if not (src == 68 and dst == 67):
            raise NotDhcpPacketError("Invalid src/dest port")

        # Looks like a DHCP request. Parse out the interesting data from the
        # base DHCP packet and check that the magic cookie is right.
        dhcp_fmt = '!12xL20x6s202xL'
        dhcp_size = struct.calcsize(dhcp_fmt)
        (xid, mac, cookie) = struct.unpack(dhcp_fmt, pkt[:dhcp_size])

        if cookie != Constants.DHCP_MAGIC_COOKIE or self.client_mac != mac:
            raise NotDhcpPacketError("Invalid magic cookie")

        self.xid = xid

        self.uuid = 'not specified'

        self._parse_dhcp_options(pkt[dhcp_size:])

    def _parse_dhcp_options(self, options):
        self.unknown_options = []
        self.is_pxe_request = False
        self.requested_ip = None
        # BOOTP Requests do no have the DCHP_OPTION_OP, so assume it's
        # Discover unless otherwise stated.
        self.op = Constants.DHCP_OP_DHCPDISCOVER

        for option, value in _dhcp_options(options):
            if option == Constants.DHCP_OPTION_OP:
                self.op = ord(value)
                # We only care about interesting "incoming" DHCP ops.
                if self.op not in (Constants.DHCP_OP_DHCPDISCOVER, Constants.DHCP_OP_DHCPREQUEST):
                    raise UninterestingDhcpPacket()
            elif (option in (Constants.DHCP_OPTION_CLIENT_UUID,
                             Constants.DHCP_OPTION_CLIENT_UUID2) and
                  len(value[1:]) == DHCP_CLIENT_UUID_LENGTH):
                # First byte of the UUID is \0
                self.uuid = _unpack_uuid(value[1:])
            elif option == Constants.DHCP_OPTION_VENDOR_CLASS_ID:
                self.vendor_class = value.decode('utf-8')
            elif option == Constants.DHCP_OPTION_REQUESTED_IP:
                self.requested_ip = _unpack_ip(value)
            else:
                # Keep them around, in case other code feels like
                # being knowledgeable.
                self.unknown_options.append((option, value))
