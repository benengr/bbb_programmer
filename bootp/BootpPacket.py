import struct
import bootp.Constants as Constants


class NotBootpPacketError(Exception):
    """Packet being decoded is not a BOOTP packet."""


class BootpPacket(object):
    def __init__(self, pkt):
        # Check the ethernet type. It needs to be IP (0x800).
        if struct.unpack('!H', pkt[12:14])[0] != Constants.ETHERNET_IP_PROTO:
            raise NotBootpPacketError()
        self.server_mac, self.client_mac = pkt[0:6], pkt[6:12]

        # Strip off the ethernet frame and check the IP packet type. It should
        # be UDP (0x11)
        pkt = pkt[14:]
        if ord(pkt[9]) != Constants.IP_UDP_PROTO:
            raise NotBootpPacketError()

        # Strip off the IP header and check the source/destination ports in the
        # UDP datagram. The packet should be from port 68 to port 67 to be
        # BOOTP. We don't care about checksum here
        header_len = (ord(pkt[0]) & 0xF) * 4
        pkt = pkt[header_len:]
        (src, dst) = struct.unpack('!2H4x', pkt[:8])
        if not (src == 68 and dst == 67):
            raise NotBootpPacketError()

        # Looks like a BOOTP request. Strip off the UDP headers, parse out the
        # interesting data from the base BOOTP packet and check that the magic
        # cookie is right.
        pkt = pkt[8:]
        bootp_fmt = '!4xL20x6s10x64s128xL'
        bootp_size = struct.calcsize(bootp_fmt)
        (xid, mac, sname, cookie) = struct.unpack(bootp_fmt, pkt[:bootp_size])

        # We strip off the padding bytes
        try:
            sname = sname[:sname.index('\x00')]
        except ValueError:
            pass

        self.sname = sname

        if cookie != Constants.BOOTP_MAGIC_COOKIE or self.client_mac != mac:
            raise NotBootpPacketError()

        self.xid = xid
