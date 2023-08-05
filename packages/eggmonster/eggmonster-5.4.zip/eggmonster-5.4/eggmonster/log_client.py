import logging
import platform

HOST = platform.node()

class EggmonsterLogHandler(logging.Handler):
    """A logging facility for eggmonster."""
    def __init__(self, host, port, facility, fail_on_socket_error=False):
        self.host = str(host)
        self.port = port
        self.facility = str(facility)
        self.fail_on_socket_error = fail_on_socket_error
        self.timeout = 8  # TODO: make configurable
        logging.Handler.__init__(self)

    def emit(self, record):
        import socket
        all_data = self.format(record)
        sock = None
        try:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(self.timeout)
                sock.connect((self.host, self.port))
                for line in all_data.splitlines():
                    sock.sendall('%s|%s|%s\r\n' % (self.facility, HOST, line))
            except socket.error:  # including socket.timeout
                if self.fail_on_socket_error:
                    raise
        finally:
            if sock:
                try:
                    sock.close()
                except:
                    pass

if __name__ == '__main__':
    import logging
    log = logging.getLogger()
    handler = EggmonsterLogHandler('localhost', 13000, 'test-service')
    handler.setLevel(logging.DEBUG)
    log.addHandler(handler)
    log.error("this is an error!")
