import struct
import bootp.Constants as Constants


class NotBootpPacketError(Exception):
    def __init__(self, msg=None):
        self.message = msg
    """Packet being decoded is not a BOOTP packet."""



class BootpPacket(object):
    def __init__(self, pkt):
        self.vendor_class = None
        # Check the ethernet type. It needs to be IP (0x800).
        if struct.unpack('!H', pkt[12:14])[0] != Constants.ETHERNET_IP_PROTO:
            raise NotBootpPacketError('Invalid Ethernet Protocol')
        self.server_mac, self.client_mac = pkt[0:6], pkt[6:12]

        # Strip off the ethernet frame and check the IP packet type. It should
        # be UDP (0x11)
        pkt = pkt[14:]
        if pkt[9] != Constants.IP_UDP_PROTO:
            raise NotBootpPacketError('Not UDP Protocol')

        # Strip off the IP header and check the source/destination ports in the
        # UDP datagram. The packet should be from port 68 to port 67 to be
        # BOOTP. We don't care about checksum here
        header_len = (pkt[0] & 0xF) * 4
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
        vendor = pkt[bootp_size:]
        self.process_vendor_specific(vendor)


        # We strip off the padding bytes
        try:
            sname = sname[:sname.index(b'\x00')]
        except ValueError:
            pass

        self.sname = sname

        if cookie != Constants.BOOTP_MAGIC_COOKIE or self.client_mac != mac:
            raise NotBootpPacketError()

        self.xid = xid

    def process_vendor_specific(self, vendor):
        index = 0
        while index <= len(vendor):
            tag = int(vendor[index])
            index += 1
            if tag == 0:
                continue
            if tag == 255:
                return
            l = int(vendor[index])
            index += 1
            v = vendor[index:index + l]
            index += l
            if tag == 60:
                self.vendor_class = bytes.decode(v, 'utf-8')
        return
