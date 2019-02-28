from TFTPServer import TFTPServer
import socketserver


server = socketserver.UDPServer(('0.0.0.0', 1234), TFTPServer)
server.serve_forever()
