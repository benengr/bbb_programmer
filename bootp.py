from bootp.BOOTPServer import BOOTPServer
import logging

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('main')
server = BOOTPServer('usb0', None, '192.168.4.1', '192.168.4.1')

done = False
while not done:
    try:
        log.info("Starting Server")
        server.serve_forever()
    except KeyboardInterrupt:
        log.info("Keyboard interrupt, shutting down")
        done = True
    except Exception as ex:
        log.exception(ex)
        log.info("restarting server")
