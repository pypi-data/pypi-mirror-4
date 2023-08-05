import cgi
import os
from cStringIO import StringIO

from eventful.proto.http import HttpServerProtocol, HttpHeaders
from eventful import Application, Service
from eventful import log
import eventful

repo = None
passdb = None

def dump_package(name, version, typ, content, pyversion, hash):
    if typ == 'sdist':
        filename = '%s-%s.tar.gz' % (name, version)
    elif typ == 'bdist_egg':
        filename = '%s-%s-py%s.egg' % (name, version, pyversion)
    else:
        raise ValueError("don't know what to do with package type %r" % typ)
    full_fn = os.path.join(repo, filename)
    assert not os.path.exists(full_fn)
    open(full_fn, 'wb').write(content)
    print "%s -> %s" % (hash, filename)

def list_repo():
    def c():
        for fn in sorted(os.listdir(repo)):
            yield '<a href="/%s">%s</a><br/>\n' % (fn, fn)
    return ''.join(list(c()))

def get_package(fn):
    path = os.path.join(repo, fn)
    if os.path.isfile(path):
        return open(path, 'rb').read()

def user_is_authorized(hash):
    db = set(l.strip() for l in open(passdb))
    return hash in db

class EggServer(HttpServerProtocol):

    def get_http_headers(self):
        heads = HttpHeaders()
        heads.add('server', 'eggserver/devel')
        return heads

    def on_HTTP_GET(self, req):
        heads = self.get_http_headers()
        if req.url == '/':
            content = list_repo()
            heads.add('content-type', 'text/html')
            heads.add('content-length', str(len(content)))
            self.send_http_response(req, '200 OK', heads, content)
        else:
            content = get_package(req.url[1:])
            if not content:
                self.send_http_response(req, '404 Not Found', heads, 'Resource Not Found')
            else:
                heads.add('content-type', 'application/octet-stream')
                heads.add('content-length', str(len(content)))
                self.send_http_response(req, '200 OK', heads, content)

    def on_HTTP_POST(self, req):
        ct, ct_extra = cgi.parse_header(req.headers['content-type'][0])
        auth_raw = req.headers['Authorization'][0]
        auth_type, hash  = auth_raw.split()

        if passdb and (auth_type != 'Basic' or not user_is_authorized(hash)):
            heads = self.get_http_headers()
            heads.add('WWW-Authenticate', 'Basic realm="eggserver"')
            return self.send_http_response(req, '401 Unauthorized', heads, '')

        data = cgi.parse_multipart(StringIO(req.body), ct_extra)
        name = data['name'][0]
        version = data['version'][0]
        content = data['content'][0]
        typ = data['filetype'][0]
        pyversion = data['pyversion'][0]

        try:
            dump_package(name, version, typ, content, pyversion, hash)
        except AssertionError:
            return self.send_http_response(req, '500 Error--Package Exists', self.get_http_headers(), '')

        self.send_http_response(req, '200 OK', self.get_http_headers(), '')

def setup_env(l_repo, l_passdb):
    global repo
    global passdb
    repo = l_repo
    passdb = l_passdb

def main(repo, passdb, port):
    setup_env(repo, passdb)
    app = Application()
    app.add_service(Service(EggServer, port))
    app.run()
