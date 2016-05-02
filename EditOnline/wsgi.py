"""
WSGI warp
"""

import os
import wsgiref.util


import EditOnline
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

class HeadsWarp(object):
    environ = None
    def __init__(self, environ):
        self.environ = environ
    def getheader(self, name):
        name = name.upper().replace('-', '_')
        return self.environ.get('HTTP_%s' % (name), self.environ.get(name))

class WSGIHandler(EditOnline.EditOnlineRequestHandler):
    path = None
    headers = None
    
    response_code = 200
    response_message = 'OK'
    request_version = 'HTTP/1.0'
    response_headermap = {
                          'Content-Type':'text/html'
                          }
    
    def __init__(self, request, client_address, server):
        self.request = request
        self.client_address = client_address
        self.server = server
        self.setup()
        try:
            self.handle()
        finally:
            self.finish()
    
    def setup(self):
        pass
    
    def finish(self):
        pass
    
    def handle(self):
        pass
    
    def handle_one_request(self):
        pass
    
    def send_response(self, code, message=None):
        self.response_code = code
        self.response_message = message
    
    def send_header(self, keyword, value):
        self.response_headermap[keyword] = value
    
    @property
    def response_headers(self):
        return self.response_headermap.items()

if os.environ.get('WSGI_PARAMS'):
    argv = [v.strip() for v in os.environ.get('WSGI_PARAMS').split(' ') if v.strip()]
    EditOnline.config(argv)

def application(environ, start_response):    
    handler = WSGIHandler(None, (environ['REMOTE_ADDR'], None), None)
#     for k, v in environ.items():
#         print k, v
    handler.path = environ['PATH_INFO'] + ('?' + environ['QUERY_STRING'] if environ['QUERY_STRING'] else '')
    handler.rfile = environ['wsgi.input']
    handler.headers = HeadsWarp(environ)
    handler.wfile = StringIO()
    handler.request_version = environ['SERVER_PROTOCOL']
    handler.command = environ['REQUEST_METHOD']
    method = 'do_%s' % (environ['REQUEST_METHOD'])
    if hasattr(handler, method):
        handler_method = getattr(handler, method)
        handler_method()
    handler.wfile.seek(0)
    res = handler.wfile.read()[2:]
    if res.startswith('\n\n'):
        res = res[2:]
    if res:
        handler.send_header("Content-Length", str(len(res)))
    
    status = '%s %s' % (handler.response_code or 200, handler.response_message or 'OK')
    headers = [(k, v) for k, v in handler.response_headers if not wsgiref.util.is_hop_by_hop(k)]
    
    start_response(status, headers)

    

    return [res, ]
