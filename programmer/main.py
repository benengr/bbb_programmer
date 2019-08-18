import threading
import logging
from bootp.DHCPServer import DHCPServer
from tftp.Server import Server
import netifaces
import time
import state.event_handler
import state.leds as leds
from logging.handlers import RotatingFileHandler


def wait_for_interface(iface, poll_time, logger, handler):
    logger.info("Waiting for %s to become available", iface)
    while True:
        logger.debug("Checking if %s exists", iface)
        if iface in netifaces.interfaces():
            try:
                logger.debug("%s exists, trying to find IP address", iface)
                return netifaces.ifaddresses(iface)[2][0]['addr']
            except ValueError:
                handler.no_connection()
            # A Key error means a USB RNDIS device has been enumerated
            # but not actually brought all the way up
            except KeyError:
                handler.unknown_system_connected()
                logger.debug("KeyError while getting address for %s", iface)
        time.sleep(poll_time)
        handler.no_connection()


def start_bootp(iface, ip, handler):
    try:
        log.info("bootp for %s on ip %s", iface, ip)
        server = DHCPServer(iface, None, ip, ip, connection_callback=handler.handle_connection)
        server.serve_forever()
    except:
        log.info('Network is disconnected')


def dhcp_thread(iface, handler):
    logging.info("starting thread %s", iface)
    while True:
        try:
            address = wait_for_interface(iface, 0.5, log, handler)
            logging.info("found interface with ip : %s", address)
            start_bootp(iface, address)
        except Exception as ex:
            log.error("unhandled exception occurred on thread %s", iface)
            log.exception(ex)


if __name__ == "__main__":
    h1 = state.event_handler.EventHandler(7, 11, 13)
    h2 = state.event_handler.EventHandler(15, 29, 31)
    h3 = state.event_handler.EventHandler(12, 16, 18)
    h4 = state.event_handler.EventHandler(22, 37, 32)

    h1.startup()

    fileSize = 1024 * 1024 * 128 # 128 MB, total of 1.5 GB
    log_handler = RotatingFileHandler('/home/pi/bbb_programing.log', maxBytes=fileSize, backupCount=5)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
    logging.getLogger().addHandler(log_handler)
    log = logging.getLogger('main')
    log.info("System Started")

    usb1_thread = threading.Thread(target=dhcp_thread, args=('usb0', h1))
    usb2_thread = threading.Thread(target=dhcp_thread, args=('usb1', h2))
    usb3_thread = threading.Thread(target=dhcp_thread, args=('usb2', h3))
    usb4_thread = threading.Thread(target=dhcp_thread, args=('usb3', h4))
    usb1_thread.start()
    usb2_thread.start()
    usb3_thread.start()
    usb4_thread.start()
    usb1_thread.join()
    usb2_thread.join()
    usb3_thread.join()
    usb4_thread.join()
    log.info("Exiting")
