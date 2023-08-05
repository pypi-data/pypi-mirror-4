import os
import posixpath
import re
import ConfigParser
import signal
import urllib
import urllib2
import json

from eggmonster import emenv, __version__

def get_authen():
    pypirc = os.path.expanduser('~/.pypirc')
    if os.path.isfile(pypirc):
        parser = ConfigParser.ConfigParser()
        parser.readfp(open(pypirc))
        try:
            username = parser.get('server-login', 'username')
            password = parser.get('server-login', 'password')
        except:
            return None
        else:
            return ('%s:%s' % (username, password)).encode('base64').strip()
    return None

# from jaraco.net.http
class MethodRequest(urllib2.Request):
    def __init__(self, *args, **kwargs):
        """
        Construct a MethodRequest. Usage is the same as for
        `urllib2.Request` except it also takes an optional `method`
        keyword argument. If supplied, `method` will be used instead of
        the default.
        """
        if 'method' in kwargs:
            self.method = kwargs.pop('method')
        return urllib2.Request.__init__(self, *args, **kwargs)

    def get_method(self):
        return getattr(self, 'method', urllib2.Request.get_method(self))

class Http():
    def request(self, url, method='GET', body=None, headers={}):
        if body and method == 'GET':
            method = 'POST'
        req = MethodRequest(url, method=method, data=body, headers=headers)
        result = urllib2.urlopen(req)
        body = result.read()
        return result, body

def make_browser():
    browser = Http()
    return browser

def getjson(url):
    server = emenv.master
    browser = make_browser()
    auth = get_authen()
    headers = {'Authorization' : 'Basic %s' % auth} if auth else {}
    headers['User-Agent'] = 'Eggmonster/%s' % __version__

    server_url = posixpath.join(server, url)
    import socket
    try:
        resp, body = browser.request(server_url, headers=headers)
    except (socket.error,), e:
        raise ValueError("Error connecting to server at %s: %s" % (server_url, e))
    if resp.code == 403:
        raise ValueError("HTTP 403 Permission Denied.. Authorization?")
    assert resp.code == 200, "Non-200 response code back from server: %s - %s" % (resp.code, server_url)
    return json.loads(body)

def putargs(url, args, method='PUT', check_status=True):
    server = emenv.master
    browser = make_browser()
    auth = get_authen()
    headers = {'Authorization' : 'Basic %s' % auth} if auth else {}
    headers['User-Agent'] = 'Eggmonster/%s' % __version__
    putbody = urllib.urlencode(args)
    resp, body = browser.request(posixpath.join(server, url), method, putbody, headers=headers)
    assert not check_status or 200 <= resp.code < 300
    return resp, body

MINFACT = 60
HOURFACT = MINFACT * 60
DAYFACT = HOURFACT * 24
def timestr(s, max=0, depth=0):
    if max and depth == max:
        return ''
    if s >= DAYFACT:
        return ('%dd ' % (s / DAYFACT)) + timestr(s % DAYFACT, max, depth+1)
    if s >= HOURFACT:
        return ('%dh ' % (s / HOURFACT)) + timestr(s % HOURFACT, max, depth+1)
    if s >= MINFACT:
        return ('%dm ' % (s / MINFACT)) + timestr(s % MINFACT, max, depth+1)
    return '%ds' % s

def stat_to_node_def(line):
    package, app, host, num = stat_line.match(line).groups()
    return package, app, host, int(num)

stat_line = re.compile(r"^(.+?)\.(.+?) \((.+):([0-9]+)\) .*$")

def stat_to_args(fd):
    nodes = [stat_to_node_def(line) for line in fd]
    return dict(node_json=json.dumps(nodes))

def control_command(fd, cmd):
    nodes = stat_to_args(fd)
    putargs(cmd, nodes, 'POST')

def reset_sigpipe():
    """
    cope with broken pipes
    """
    if hasattr(signal, 'SIGPIPE'):
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)

def reset_sigint():
    "handle keyboard interrupts nicely"
    signal.signal(signal.SIGINT, signal.SIG_DFL)

