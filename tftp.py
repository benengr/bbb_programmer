from tftp.Server import Server
import logging


def run_server():
    iface = '0.0.0.0'
    root = '/var/tftproot'
    port = 69 

    server = Server(iface, root, port)
    server.serve_forever()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    run_server()

