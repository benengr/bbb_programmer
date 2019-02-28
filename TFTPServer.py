import socketserver
from tftp import proto
import logging


log = logging.getLogger('tftp')


class TFTPServer(socketserver.DatagramRequestHandler):
    def handle(self):
        log.info("inside handle")
        request = self.request[0].strip()

        # Get the packet opcode and dispatch
        opcode = proto.TFTPHelper.get_opcode(request)

        log.info('{} wrote:'.format(self.client_address[0]))
        log.info(request)
        log.info('opcode is {}'.format(opcode))
