import threading
import logging
from bootp.BOOTPServer import BOOTPServer
from tftp.Server import Server
import netifaces
import time

IFACE = 'usb0'
TFTP_ROOT = '/var/tftproot'
TFTP_PORT = 69


def wait_for_interface(iface, poll_time, logger):
    logger.info("Waiting for %s to become available", iface)
    while True:
        logger.debug("Checking if %s exists", iface)
        if iface in netifaces.interfaces():
            try:
                logger.debug("%s exists, trying to find IP address", iface)
                return netifaces.ifaddresses(iface)[2][0]['addr']
            except ValueError as error:
                logger.error("Could not get an address for %s", iface)
                logger.exception(error)
                pass
        time.sleep(poll_time)


def start_bootp(ip):
    server = BOOTPServer(IFACE, None, ip, ip)
    server.serve_forever()


def start_tftp(ip):
    server = Server(ip, TFTP_ROOT, TFTP_PORT)
    server.serve_forever()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    log = logging.getLogger('main')
    log.info("System Started")
    bootp_thread = None
    tftp_thread = None
    try:
        while True:
            address = wait_for_interface(IFACE, 1, log)
            print(address)
            thread_args = (address,)
            logging.info("found interface with ip: %s", address)
            if bootp_thread is None:
                bootp_thread = threading.Thread(target=start_bootp, args=thread_args)
                log.info("Starting bootp thread")
                bootp_thread.start()
            if tftp_thread is None:
                tftp_thread = threading.Thread(target=start_tftp, args=thread_args)
                log.info("Starting tftp thread")
                tftp_thread.start()
            log.info("Waiting for threads to complete")
            bootp_thread.join()
    except Exception as ex:
        log.error("unhandled exception occurred")
        log.exception(ex)
    log.info("Exiting")
