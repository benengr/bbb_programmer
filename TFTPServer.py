import socketserver


class TFTPServer(socketserver.DatagramRequestHandler):
    def handle(self):
        data = self.request[0].strip()
        print('{} wrote:'.format(self.client_address[0]))
        print(data)
