from bootp.BOOTPServer import BOOTPServer
import logging


def run_server():
    log = logging.getLogger('bootpthread')
    server = BOOTPServer('usb0', None, '192.168.4.1', '192.168.4.1')
    done = False
    while not done:
        try:
            log.info("Starting server")
            server.serve_forever()
        except KeyboardInterrupt:
            done = True
        except Exception as ex:
            log.info("Restarting Server")
            pass


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    run_server()
