from bootp.BOOTPServer import BOOTPServer
import logging

logging.basicConfig(level=logging.DEBUG)

server = BOOTPServer('usb0', None, '192.168.4.1', '192.168.4.1')
server.serve_forever()
