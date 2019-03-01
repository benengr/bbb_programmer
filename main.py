import threading
import logging
from bootp.BOOTPServer import BOOTPServer
from tftp.Server import Server


def start_bootp():
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


def start_tftp(iface, root, port):
    server = Server(iface, root, port)
    server.serve_forever()


if __name__ == "__main__":
    bootp_thread = threading.Thread(target=start_bootp)
    tftp_thread = threading.Thread(target=tftp_thread)
    logging.info("Starting bootp thread")
    bootp_thread.run()
    logging.info("Starting tftp thread")
    tftp_thread.run()
    logging.info("Joining threads")
    bootp_thread.join()
    tftp_thread.join()
    logging.info("Exiting")
