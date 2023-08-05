import os
import logging
import socket
import threading
import signal
import json

try:
    import fcntl
    import pwd
except ImportError:
    pass

from eggmonster import packages
from eggmonster import emenv

HOSTNAME = os.environ.get('EMI_ME')

logger = logging.getLogger('em.emi.parent')

def get_app_info(sock):
    ret = sock.recv(65536)
    if not ret:
        logger.info('Server closed connection before launch.')
        raise SystemExit(0)
    l, buf = ret.split('|', 1)
    l = int(l)
    while len(buf) < l:
        ret = sock.recv(65536)
        if not ret:
            logger.info('Server closed connection before launch.')
            raise SystemExit(0)
        buf += ret

    raw_info, buf = buf[:l], buf[l:]

    app_info = json.loads(raw_info)

    return app_info, buf

def sendsig(child, sig):
    signal_name = {signal.SIGKILL: 'KILL', signal.SIGTERM: 'TERM'}.get(
        sig, 'SIG%s' % sig)
    logger.debug('Sending %s signal to child process.' % signal_name)
    os.kill(child, sig)

def process_server_commands(sock, buf, child):
    while True:
        while '\n' not in buf:
            try:
                ret = sock.recv(65536)
                if not ret:
                    raise Exception()
                buf += ret
            except:
                # Connection to the Eggmonster master has been lost.
                #
                # Existing services will not be able to continue to be
                # managed by the master, so they necessarily need to be
                # stopped (it would be nice if they did not).
                # If the master restarts, it should respawn this
                # parent process.
                #
                # Send a TERM signal (and not KILL) to politely ask the
                # child process to terminate. It may continue to run and
                # finish any open processing (or hang indefinitely if it
                # does not behave well).
                logger.info('Connection to master dropped, terminating.')
                sendsig(child, signal.SIGTERM)
                raise SystemExit(0)

        cmd, buf = buf.split('\n', 1)
        cmd = cmd.strip()
        if cmd == 'noop':
            pass
        elif cmd == 'term':
            sendsig(child, signal.SIGTERM)
        elif cmd == 'kill':
            sendsig(child, signal.SIGKILL)

def connect_to_master():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if 'fcntl' in globals():
        fcntl.fcntl(sock, fcntl.FD_CLOEXEC, 1)
    sock.connect((emenv.master_host, emenv.master_emi_port))
    return sock

def get_config(HOSTNAME, app_name, app_num, flags):
    sock = connect_to_master()
    sock.sendall('%s %s %s %s\r\n' % (HOSTNAME, app_name, app_num, flags))
    (entry_point, env, pkg_info), buf = get_app_info(sock)
    return entry_point, env, pkg_info, buf, sock

def main(app_name, num, spawn_app, extra_args, debug):

    app_id = ', appid=%s:%s' % (app_name, num)

    import eggmonster.internal_log
    eggmonster.internal_log.configure(debug, app_id)

    logger.debug('Launching.')

    try:
        _main(app_name, num, spawn_app, extra_args)
    finally:
        logger.debug('Exiting.')

def _main(app_name, num, spawn_app, extra_args):
    master_user = os.environ['EMI_USER']
    master_uid = pwd.getpwnam(master_user)[2]

    # upper case - flag enabled
    # lower case - flag disabled
    flags = ''.join([
        'm' if spawn_app else 'M', # monitored by eggmaster
    ])

    entry_point, env, pkg_info, buf, sock = get_config(HOSTNAME, app_name,
        num, flags)

    packages.load_dependencies(pkg_info, packages.install)
    if not master_uid == os.getuid():
        os.setuid(master_uid)

    # If the below line returns (and does not raise a SystemExit), then this
    # means we are the master emi process and we communicate between the
    # eggmaster and forked child process.
    child = run_app(pkg_info, entry_point, env, num, spawn_app, extra_args)

    # This will communicate between the Eggmaster and the child process.
    thread = threading.Thread(target=process_server_commands,
        args=(sock, buf, child))
    thread.setDaemon(True)
    thread.start()

    # If the parent process is sent the terminate signal outside of
    # Eggmonster, we want to send that signal to the child process.
    def handler(signum, frame):
        logger.debug('Being forced to terminate, telling child process '
            'to terminate too.')
        os.kill(child, signal.SIGTERM)
        raise SystemExit(0)

    signal.signal(signal.SIGTERM, handler)

    try:
        res = os.waitpid(child, 0)[1]
    except:
        logger.exception('Error while waiting for child process.')
        os.kill(child, signal.SIGTERM)
        raise

    logger.debug('Child process stopped: exitcode=%s, signalled=%s',
        os.WEXITSTATUS(res), os.WIFSIGNALED(res))

def run_app(pkginfo, entry_point, env, num, spawn_app, extra_args):
    if not spawn_app:
        pid = os.fork()
        if pid:
            logger.debug('Spawned child process with pid %s.' % pid)
            return pid

    # update the logger to indicate we're now in a child process
    globals().update(logger = logging.getLogger('em.emi.child'))

    logger.debug('About to locate entry point "%s" in package "%s".',
        (spawn_app or entry_point), pkginfo)

    from eggmonster import update_locals, _set_managed_env
    _set_managed_env()
    env = fill_config_placeholders(env, num)
    update_locals(env)
    pkg = packages.load_dependencies(pkginfo)
    app_func = pkg.load_entry_point('eggmonster.applications',
        spawn_app or entry_point)

    logger.debug('Found entry point, running.')

    from eggmonster.runner import can_take_app_args
    if can_take_app_args(app_func):
        app_func(spawn_app or entry_point, extra_args)
    else:
        app_func()

    logger.debug('Entry point function returned, terminating.')
    raise SystemExit(0)

from string import Template

def fill_config_placeholders(env, num):
    fill_dict = {
        'num': num,
        'host': HOSTNAME,
    }
    env = env.copy()
    for k, v in env.items():
        if isinstance(v, basestring) and '$' in v:
            v = Template(v).safe_substitute(fill_dict)
            if v.isdigit():
                v = int(v)
        env[k] = v
    return env
