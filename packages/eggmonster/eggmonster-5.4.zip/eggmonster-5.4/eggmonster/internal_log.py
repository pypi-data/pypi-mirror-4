import logging
import sys
import os
import socket

import eggmonster

def get_host():
    """
    Determine a good host for eggmonster logging. Log to the host specified
    by EGGMONSTER_LOG_HOST if defined in the environment, or log to 
    `monster-log` if it resolves.
    """
    env_host = os.environ.get('EGGMONSTER_LOG_HOST')
    if env_host:
        host, sep, port = env_host.partition(':')
        port = int(port) if port else eggmonster.logger_port
    else:
        try:
            socket.gethostbyname('eggmonster-log')
            host = 'eggmonster-log'
            port = eggmonster.logger_port
        except socket.gaierror:
            return None
    return host, port

def configure(debug_flag, extra_identity=''):
    logger = logging.getLogger('em')
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%%(name)s [pid=%%(process)s%s] %%(message)s' % extra_identity)

    # Set up stderr handler.
    sys_handler = logging.StreamHandler(sys.stderr)
    sys_handler.setFormatter(formatter)
    sys_handler.setLevel(logging.DEBUG if debug_flag else logging.INFO)
    logger.addHandler(sys_handler)

    log_host = get_host()
    if not log_host: return
    host, port = log_host

    from eggmonster.log_client import EggmonsterLogHandler
    em_handler = EggmonsterLogHandler(host, port, 'eggmonster',
        fail_on_socket_error=debug_flag)
    em_handler.setFormatter(formatter)
    em_handler.setLevel(logging.DEBUG)
    logger.addHandler(em_handler)
