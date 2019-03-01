from tftp.Server import Server
import logging


def run_server():
    iface = '127.0.0.1'
    root = '/Users/benanderson/tftp'
    port = 4234

    server = Server(iface, root, port)
    server.serve_forever()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    run_server()

