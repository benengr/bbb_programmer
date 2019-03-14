from unittest import TestCase
from bootp.IpGenerator import IpGenerator
from bootp.Utilities import _unpack_ip, _pack_ip
from struct import pack


def int_to_ip(val):
    packed = pack('!L', val)
    return _unpack_ip(packed)


class TestIPGenerator(TestCase):
    def test_pack(self):
        ip = "192.168.2.3"
        out = _pack_ip(ip)
        done = _unpack_ip(out)
        self.assertEqual(ip, done)

    def test_init(self):
        ip = "192.168.5.1"
        netmask = "255.255.255.0"
        gen = IpGenerator(ip, netmask)
        self.assertEqual(ip, int_to_ip(gen.server_ip))
        self.assertEqual(netmask, int_to_ip(gen.netmask))

    def test_zero(self):
        gen = IpGenerator("192.168.4.1", "255.255.255.0")
        ip = gen.generate_ip(0)
        self.assertFalse(gen.is_ip_valid(ip))

    def test_bcast(self):
        gen = IpGenerator("192.168.4.1", "255.255.255.0")
        ip = gen.generate_ip(0xFFFFFFFF)
        self.assertFalse(gen.is_ip_valid(ip))
