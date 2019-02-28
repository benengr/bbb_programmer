import socketserver
from tftp import proto
import logging


log = logging.getLogger('tftp')


class TFTPServer(socketserver.DatagramRequestHandler):
    def handle(self):
        TFTPServer.handle_request(self.request[0].strip(), self)

    def send_response(self, response):
        """
        Send a response to the client
        :param response (bytes or tuple): the response packet sequence.  If the
            argument is a simple bytestring object, it is sent as-is. If it is
            a tuple, it is expected to be a 2-uple containing first a
            bytestring packet, and second a function that, when called, returns
            the next packet sequence to send through this method (recursively).
        """
        while response:
            if type(response) == tuple:
                message, response = response[0], response[1]()
            else:
                message, response = response, None

            self.wfile.write(message)
            self.wfile.flush()

    @staticmethod
    def handle_request(request, server):
        log.info("inside handle")

        # Get the packet opcode and dispatch
        opcode = proto.TFTPHelper.get_opcode(request)
        if not opcode:
            log.error('Can\'t find opcode, packet ignored')
            return

        if opcode not in proto.TFTP_OPS:
            log.error('Unknown operation %d', opcode)
            response = proto.TFTPHelper.createERROR(proto.ERROR_ILLEGAL_OP)
            server.send_response(response)
            return

        log.info('{} wrote:'.format(server.client_address[0]))
        log.info(request)
        log.info('opcode is {}'.format(opcode))
        server.send_response(bytes("good", 'utf-8'))
