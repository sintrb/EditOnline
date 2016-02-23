# -*- coding: UTF-8 -*
'''
@author: sintrb
'''
__version__ = "0.1"


import SimpleHTTPServer
import SocketServer


class EditHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
	server_version = "EditOnline/" + __version__

# HandlerClass = SimpleHTTPRequestHandler
Protocol = "HTTP/1.0"


PORT = 8000
httpd = SocketServer.TCPServer(("", PORT), EditHandler)

print "EditOnline at port", PORT
httpd.serve_forever()


