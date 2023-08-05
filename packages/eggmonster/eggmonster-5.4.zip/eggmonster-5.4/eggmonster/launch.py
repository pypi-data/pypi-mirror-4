import logging
import os
import platform
from subprocess import Popen
import socket
import traceback
import time

from pkg_resources import require

from eggmonster import packages
from eggmonster import emenv
import eggmonster.internal_log

EM_VERSION = require('eggmonster')[0].version

def main(user, debug, host_id=None):
    eggmonster.internal_log.configure(debug)

    logger = logging.getLogger('em.launchd')
    if host_id is None:
        host_id = platform.node()
    os.environ['EMI_ME'] = host_id
    os.environ['EMI_USER'] = user

    logger.debug('launchd process started - host id: "%(host_id)s"' % vars())

    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            sock.connect((emenv.master_host, emenv.master_launch_port))

            version = sock.recv(32).strip()
            if version == '':
                raise socket.error()
            if version != EM_VERSION:
                logger.info('Eggmonster upgrade from %s to %s '
                    'required...', EM_VERSION, version)
                pkg_spec = 'eggmonster == %(version)s' % vars()
                packages.install(pkg_spec, multi=False)
                raise SystemExit()

            sock.sendall(host_id + '\r\n')
            launch_loop(sock, debug)
        except socket.error:
            traceback.print_exc()
            logger.info('Resetting connection to master in 5 seconds...')
            time.sleep(5)

def launch_loop(sock, debug):
    sockfile = sock.makefile('r', 1)
    for line in sockfile:
        if line.strip() != 'noop':
            launch_app(line, debug)

# Usefully nabbed from:
#   http://jimmyg.org/blog/2009/working-with-python-subprocess.html
def whereis(program):
    paths = os.environ.get('PATH', '').split(os.pathsep)
    for path in paths:
        target = os.path.join(path, program)
        if os.path.exists(target) and not os.path.isdir(target):
            return target
    return None

def launch_app(line, debug):
    try:
        app_id, n, package = line.strip().split(None, 2)
    except ValueError:
        raise ValueError("Unrecognized application spec %r" % line)
    args = ["emi", app_id, n]
    if debug:
        args.insert(1, '--debug')

    logger = logging.getLogger('em.launchd')

    try:
        proc = Popen(args)
    except OSError:
        logger.error('Problem invoking process: %s' % (args,))
        if not whereis('emi'):
            logger.error('Could not find "emi" executable on path: %s' % os.environ.get('PATH', ''))
        raise

    logger.debug('Running "%s" [pid=%s]' % (' '.join(args), proc.pid))
