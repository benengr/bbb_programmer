# The IP protocol number in Ethernet frames.
ETHERNET_IP_PROTO = 0x800

# The UDP protocol number in IP datagrams.
IP_UDP_PROTO = 0x11

# DHCP operation types. There are others, but we don't care.
DHCP_OP_DHCPDISCOVER = 1
DHCP_OP_DHCPOFFER = 2
DHCP_OP_DHCPREQUEST = 3
DHCP_OP_DHCPACK = 5

# The DHCP magic cookie value that precedes option fields.
DHCP_MAGIC_COOKIE = 0x63825363

# DHCP options we care about.
DHCP_OPTION_SUBNET = 1                # Subnet mask
DHCP_OPTION_ROUTER = 3                # Router
DHCP_OPTION_DNS = 6                   # Domain Name Servers (DNS)
DHCP_OPTION_REQUESTED_IP = 50         # Requested IP address
DHCP_OPTION_LEASE_TIME = 51           # Lease time for the IP address
DHCP_OPTION_OP = 53                   # The DHCP operation (see above)
DHCP_OPTION_SERVER_ID = 54            # Server Identifier (IP address)
DHCP_OPTION_VENDOR_CLASS_ID = 60      # The vendor class identifier, used
                                      # to identify PXE clients
DHCP_OPTION_CLIENT_UUID = 61          # The client machine UUID
DHCP_OPTION_PXE_VENDOR = 43           # PXE vendor extensions
DHCP_OPTION_CLIENT_UUID2 = 97         # The client machine UUID