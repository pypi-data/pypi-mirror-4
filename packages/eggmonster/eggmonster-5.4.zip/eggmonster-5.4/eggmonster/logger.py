from eventful import Application, Service, MessageProtocol, call_every
from datetime import datetime
import os

class Logger(object):
    def __init__(self, d, write_timestamp=True):
        self.base = d
        self.write_timestamp = write_timestamp
        self.fds = {}
        self.date = None
        self.update_time()
        call_every(0.5, self.update_time)

    def update_time(self):
        now = datetime.now()
        self.timestr = now.strftime('%Y-%m-%d %H:%M:%S %Z').strip()
        date_was = self.date
        self.date = now.strftime('%Y-%m-%d')
        if self.date != date_was:
            self.fds = {}

    def log(self, pfx, msg, host=None):
        try:
            fd = self.fds[pfx]
        except KeyError:
            fd = open(os.path.join(self.base, '%s-%s.log' % (pfx, self.date)), 'a', 1)
            self.fds[pfx] = fd

        if host:
            msg = "{%s} %s" % (host, msg)

        if self.write_timestamp:
            fd.write('[%s] %s\n' % (self.timestr, msg))
        else:
            fd.write('%s\n' % (msg,))

class LogProtocolHandler(MessageProtocol):
    def on_init(self):
        self.set_readable(True)
        self.add_signal_handler('prot.message', self.message_in)

    def message_in(self, ev, msg):
        prefix, host, msg = msg.strip().split('|', 2)
        logger.log(prefix, msg, host=host)


def main(basedir, options):
    global logger
    logger = Logger(basedir, options.timestamp)
    application = Application()
    application.add_service(Service(LogProtocolHandler, options.port))
    application.run()
