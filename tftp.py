from tftp.Server import Server
import logging

logging.basicConfig(level=logging.DEBUG)

iface = 'lo0'
root = '/Users/benanderson/tftp'
port = 4234

server = Server(iface, root, port)
server.serve_forever()
