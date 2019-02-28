import socketserver
from tftp import proto


class TFTPServer(socketserver.DatagramRequestHandler):
    def handle(self):
        request = self.request[0].strip()

        # Get the packet opcode and dispatch
        opcode = proto.TFTPHelper.get_opcode(request)

        print('{} wrote:'.format(self.client_address[0]))
        print(request)
        print('opcode is {}'.format(opcode))


