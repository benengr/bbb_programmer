from TFTPServer import TFTPServer
import socketserver
import logging

logging.basicConfig(level=logging.DEBUG)
print('creating server')
server = socketserver.UDPServer(('localhost', 4234), TFTPServer)
print('serving')
server.serve_forever()
print('closing')