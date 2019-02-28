from tftp.Server import Server

server = Server('0.0.0.0', '/var/tftproot')
server.serve_forever()
