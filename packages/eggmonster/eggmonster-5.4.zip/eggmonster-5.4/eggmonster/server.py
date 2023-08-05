import os
import time
import traceback
import optparse
import functools
import json
from datetime import datetime

from eventful.proto.http import RESTServer
from eventful import log, MessageProtocol, call_every
import eventful
from pkg_resources import require

from eggmonster import config
from eggmonster.state import RunningState

EM_VERSION = require('eggmonster')[0].version

g_config = None
g_config_path = None
state = RunningState()
launch_conns = {}
emi_conns = {}

class AuthChecker(object):
    def check(self, req):
        return self.parse_auth(req) in self

    def parse_auth(self, req):
        """
        Handles basic auth
        """
        try:
            auth_raw = req.headers['Authorization'][0]
        except KeyError:
            return
        auth_type, hash = auth_raw.split()
        if not auth_type.lower() == 'basic':
            return
        return hash

    @classmethod
    def authorized(cls, f):
        """
        A decorator for an eventful HTTP server method. Determines if the
        request was authorized and returns if not.
        cls must be initialized (via init) before any
        such decorated methods are invoked.
        """
        @functools.wraps(f)
        def wrapper(self, evt, req, *args, **kw):
            if not cls.instance.check(req):
                return 403
            return f(self, evt, req, *args, **kw)
        return wrapper

    @classmethod
    def init(cls, filename):
        cls.instance = FileAuthChecker(filename) if filename else NullAuthChecker()

class FileAuthChecker(AuthChecker):
    """
    Checks users against a list of hashes
    """
    def __init__(self, filename):
        self.filename = filename

    def __contains__(self, user):
        return user in self.users()

    def users(self):
        return set(l.strip() for l in open(self.filename))

class NullAuthChecker(AuthChecker):
    """
    Always authorize the user (even None)
    """
    def __contains__(self, user):
        return True

last_sync = 0
SYNC_EVERY = 8
SYNC_CALL_PERIOD = 10
HEARTBEAT_EVERY = 30

def sync_state(force=False, check_conf_diff=False):
    global last_sync
    sync_due = time.time() - last_sync > SYNC_EVERY
    if not force or not sync_due:
        # nothing to do at the moment
        return
    for host, node in state.kill_check(check_conf_diff=check_conf_diff):
        key = (host, node.app_name, node.n)
        if key in emi_conns:
            emi_conns[key].term()
    for conn in launch_conns.values():
        conn.send_launch_info()
    last_sync = time.time()

class EggmonsterControlServer(RESTServer):
    def on_init(self):
        RESTServer.on_init(self)
        self.log = log.get_sublogger('eggmonster-server', verbosity=eventful.LOGLVL_INFO)
        self.add_signal_handler('rest.PUT.config', self.put_config)
        self.add_signal_handler('rest.GET.config', self.get_config)
        self.add_signal_handler('rest.GET.config_files', self.get_config_details)
        self.add_signal_handler('rest.GET.status', self.get_status)

        self.add_signal_handler('rest.POST.term', self.post_term)
        self.add_signal_handler('rest.POST.kill', self.post_kill)

    @AuthChecker.authorized
    def put_config(self, evt, req, *args, **kw):
        if 'last_version' in kw and int(kw['last_version'][0]) != latest_config():
            return 403, "text/plain", "Server-side config has changed; please update"
        cfg_content = kw['config'][0]
        try:
            update_config(cfg_content)
            sync_state(force=True, check_conf_diff=int(kw.get('allow_restart', [1])[0]))
        except:
            delete_latest_config()
            return 500, "text/plain", (
            "An error occured while processing your configuration:\n" + traceback.format_exc())
        return 202

    @AuthChecker.authorized
    def get_config(self, evt, req, *args, **kw):
        rev, = kw.get('revision', [latest_config()])
        jsonp_callback, = kw.get('callback', [None])
        data = json.dumps([rev, config_contents(rev)])
        if jsonp_callback:
            script = "%(jsonp_callback)s(%(data)s);" % vars()
            return 200, 'text/javascript', script
        return 200, 'application/json', data

    @AuthChecker.authorized
    def get_config_details(self, evt, req, *args, **kw):
        jsonp_callback, = kw.get('callback', [None])
        def dthandler(obj):
            if hasattr(obj, 'isoformat'):
                return obj.isoformat()
            fmt = 'Object of type %s with value of %r is not JSON serializable'
            raise TypeError, fmt % (type(obj), obj)
        data = json.dumps(config_files(), default=dthandler)
        if jsonp_callback:
            script = "%(jsonp_callback)s(%(data)s);" % vars()
            return 200, 'text/javascript', script
        return 200, 'application/json', data

    @AuthChecker.authorized
    def get_status(self, evt, req, *args, **kw):
        status = state.status
        client_version = self._get_client_version(req)

        if client_version is not None:

            # Pre 4.1.22 clients will expect a tuple of information, not a dict.
            if client_version < (4, 1, 22):
                status = (((x['host'], x['app_name'], x['num']),
                        (x.get('launchtime', 0), x.get('conf_sync', True))) for x in status)

            # For older clients, they won't be able to handle the three component name
            # (pkg.app.instance), so filter those out altogether.
            if client_version <= (4, 1, 17):
                from itertools import ifilter
                status = ifilter(lambda x: x[0][1].count('.') == 1, status)

        return 200, 'application/json', json.dumps((time.time(), list(status)))

    @AuthChecker.authorized
    def post_kill(self, evt, req, *args, **kw):
        self.cmd_on_nodes('kill', kw)
        return 202

    @AuthChecker.authorized
    def post_term(self, evt, req, *args, **kw):
        self.cmd_on_nodes('term', kw)
        return 202

    def cmd_on_nodes(self, command, kw):
        nodes = json.loads(kw['node_json'][0])
        for pkg, app, host, num in nodes:
            app_name = '%s.%s' % (pkg, app)
            num = int(num)
            key = (host, app_name, num)
            if key in emi_conns:
                getattr(emi_conns[key], command)()

    def _get_client_version(self, req):
        if not req.headers['User-Agent']:
            return None

        version_str = req.headers['User-Agent'][0][11:]
        def int_part(x):
            try:
                return int(x)
            except ValueError:
                return x
        return tuple(int_part(x) for x in version_str.split('.'))

class Cache(object):
    def __init__(self, time=5):
        self.time = time
        self._c = {}

    def touch(self, k):
        self._c[k] = time.time()

    def remove(self, k):
        if k in self._c:
            del self._c[k]

    def __contains__(self, k):
        if k not in self._c:
            return False
        tm = self._c[k]
        if time.time() - tm < self.time:
            return True
        return False

launch_reqs = Cache()

class EggmonsterLaunchServer(MessageProtocol):
    def on_init(self):
        self.set_readable(True)
        self.add_signal_handler('prot.message', self.on_message)
        self.add_signal_handler('prot.disconnected', self.on_disconnected)
        self.write(EM_VERSION.ljust(32))
        self.host = None

    def on_message(self, ev, data):
        self.host = data.strip()
        self.send_launch_info()
        launch_conns[self.host] = self

    def send_launch_info(self):
        for node in state.launch_check(self.host):
            if node.key not in launch_reqs:
                launch_reqs.touch(node.key)
                self.write('%s %s %s\r\n' % (node.app_name, node.n, node.pkginfo))

    def on_disconnected(self, ev):
        if self.host and self.host in launch_conns:
            del launch_conns[self.host]

    def noop(self):
        self.write('noop\r\n')

# This function parses the flag string passed by an emi process and
# returns an object which provides the flags as attributes on the
# resulting object - or returns None if something is wrong with the
# flags given.
#
# Because of the way flags are passed (single characters), we just
# parse it like a command line argument. Upper-case characters mean
# feature enabled, lower-case characters mean feature disabled.
#
# The flags defined in this function are kept in sync with the code
# in _em_emi.py.
def parse_flags(flags):

    # Custom error handler code - if anything is wrong with the
    # flags, then just raise a RuntimeError, catch it, and return
    # None. We can't just avoid monkeypatching and catch the SystemExit
    # raised, because the default behaviour of error is to print usage
    # information to stdout / stderr before raisiny a SystemExit.
    parser = optparse.OptionParser()
    def error(message):
        raise RuntimeError(message)
    parser.error = error

    # Helper function to populate the parser
    def add_flag(flagchar, flagname, default):
        parser.add_option(
                '-%s' % flagchar.lower(), action='store_false',
                default=default, dest=flagname)
        parser.add_option(
                '-%s' % flagchar.upper(), action='store_true',
                default=default, dest=flagname)

    # Is the process monitored by the eggmonster server?
    add_flag('m', 'monitor', True)

    try:
        options, args = parser.parse_args(['-' + flags])
    except RuntimeError:
        return None
    else:
        return options


class EggmonsterEmiServer(MessageProtocol):
    def on_init(self):
        self.set_readable(True)
        self.add_signal_handler('prot.message', self.on_message)
        self.add_signal_handler('prot.disconnected', self.on_disconnected)
        self.ni = None
        self.key = None
        self.host = None

    def on_message(self, ev, data):
        data = data.strip()
        self.host, app_name, n, flags = data.split()
        n = int(n)
        flags = parse_flags(flags)

        # This means that the flag strings given were invalid.
        if flags is None:
            self.disconnect()
            return

        # Check to see if we already have an instance running.
        if flags.monitor:
            self.key = self.host, app_name, n
            if self.key in emi_conns:
                self.disconnect()
                return

        # Locate application config.
        try:
            app_id, env, pkginfo, options = g_config.apps[app_name]
        except KeyError:
            # App not found in config?
            self.disconnect()
            return

        if flags.monitor:
            self.ni = config.NodeInfo(app_name, n, app_id, env, options, pkginfo)
            if self.ni.key not in g_config.host_nodes[self.host]:
                # This node should no longer be running this app (timing issue)?
                self.disconnect()
                return

            launch_reqs.remove(self.key)
            emi_conns[self.key] = self
            state.node_started(self.host, self.ni)

        ser_out = json.dumps((app_id, env, pkginfo))
        self.write('%s|%s' % (len(ser_out), ser_out))

    def on_disconnected(self, ev):
        if self.ni:
            state.node_stopped(self.host, self.ni)
        if self.key and self.key in emi_conns:
            del emi_conns[self.key]
        if self.host and self.host in launch_conns:
            launch_conns[self.host].send_launch_info()

    def term(self):
        self.write('term\r\n')

    def kill(self):
        self.write('kill\r\n')

    def noop(self):
        self.write('noop\r\n')

def update_config(contents):
    global g_config
    lc = latest_config()
    lc += 1
    fn = config_fn(lc)
    open(fn, 'w').write(contents)
    g_config = config.ClusterConfig.from_file(fn)
    state.update_config(g_config)

def delete_latest_config():
    num = latest_config()
    os.remove(config_fn(num))

def initial_config(d):
    global g_config_path
    global g_config
    g_config_path = d
    lc = latest_config()
    if not lc:
        update_config('')
    else:
        fn = config_fn(lc)
        g_config = config.ClusterConfig.from_file(fn)
        state.update_config(g_config)

def refresh_config():
    """
    Compare the running config (g_config) against the latest config on
    the file system. If different, update the config and state.
    """
    global g_config
    config_ = config.ClusterConfig.from_file(config_fn(latest_config()))
    if config_ == g_config:
        # nothing's changed, so do nothing
        return
    log.warn("Local config change detected; updating server config")
    g_config = config_
    state.update_config(g_config)
refresh_config.interval = 60

def config_fn(num):
    return os.path.join(g_config_path, '%s.yaml' % num)

def _file_details(filename):
    filepath = os.path.join(g_config_path, filename)
    name, ext = os.path.splitext(filename)
    number = int(name)
    mod_time = datetime.utcfromtimestamp(os.stat(filepath).st_mtime)
    return dict(
        name = filename,
        number = number,
        datetime = dict(
            date = mod_time.date(),
            time = mod_time.time(),
        ),
    )

def config_files():
    return [_file_details(name) for name in os.listdir(g_config_path)]

def config_nums():
    return [f['number'] for f in config_files()]

def latest_config():
    nums = config_nums() + [0]
    return max(nums)

def config_contents(num):
    fn = config_fn(num)
    return open(fn).read()

passdb = None

def heartbeat():
    for l_c in launch_conns.itervalues():
        l_c.noop()

    for e_c in emi_conns.itervalues():
        e_c.noop()

def main(server_config_path, port, passwd):
    AuthChecker.init(passwd)
    from eventful import Application, Service
    initial_config(server_config_path)
    app = Application()
    app.add_service(Service(EggmonsterControlServer, port))
    app.add_service(Service(EggmonsterLaunchServer, port + 1))
    app.add_service(Service(EggmonsterEmiServer, port + 2))
    call_every(SYNC_CALL_PERIOD, sync_state)
    call_every(HEARTBEAT_EVERY, heartbeat)
    # Every 60 seconds, check the file system in case config was updated by
    #  another process.
    call_every(refresh_config.interval, refresh_config)
    app.run()
