#!/usr/bin/env python
# -*- coding: UTF-8 -*
'''
@author: sintrb
'''
"""EditOnline Server.

This module refer to SimpleHTTPServer

"""


__version__ = "0.1.11"

import os
import posixpath
import BaseHTTPServer
import SocketServer
import socket
import urllib
import urlparse
import cgi
import sys
import shutil
import mimetypes
import json
try:
	from cStringIO import StringIO
except ImportError:
	from StringIO import StringIO

libdir = os.path.dirname(__file__)
if not libdir:
	libdir = os.getcwd()

options = {
		'workdir':os.getcwd(),
		'bind':'0.0.0.0',
		'port':8000
		}




class EditOnlineRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
	server_version = "EditOnline/" + __version__
	protocol_version = "HTTP/1.1"
	editortmpl = ''
	def check_auth(self):
		if not options.get('auth'):
			return True
		au = self.headers.getheader('authorization')
		if au and len(au) > 6 and au.endswith(options.get('auth')):
			return True
		self.send_response(401, "Unauthorized")
		self.send_header("Content-Type", "text/html")
		self.send_header("WWW-Authenticate", 'Basic realm="%s"' % (options.get('realm') or self.server_version))
		self.send_header('Connection', 'close')
		self.end_headers()
		return False
	
	def do_GET(self):
		if not self.check_auth():
			return
		
		f = self.send_head()
		if f:
			try:
				self.copyfile(f, self.wfile)
			finally:
				f.close()

	def do_POST(self):
		if not self.check_auth():
			return
		
		self.path = self.path.replace('..', '')

		length = int(self.headers.getheader('content-length'))
		body = self.rfile.read(length)
		path = self.translate_path(self.path).replace('~editor', '')
		if not os.path.exists(os.path.dirname(path)):
			os.makedirs(os.path.dirname(path))
		try:
			with open(path, 'wb') as f:
				f.write(body)
		except:
			self.send_error(404, "No permission to list directory")
		
		f = StringIO()
		f.write(json.dumps({
						'ok':True
						}))
		
		self.send_response(200)
		self.send_header("Content-type", 'text/json')
		self.send_header("Content-Length", str(f.tell()))
		self.end_headers()
		f.seek(0)
		try:
			self.copyfile(f, self.wfile)
		finally:
			f.close()

	def send_head(self):
		self.path = self.path.replace('..', '')
		path = self.translate_path(self.path)
		f = None
		# print self.path
		if self.path.endswith('~editor'):
			editortmplfile = os.path.join(libdir, 'editor.html')
			if not EditOnlineRequestHandler.editortmpl or True:
				try:	
					EditOnlineRequestHandler.editortmpl = ''.join(open(editortmplfile).readlines())
				except IOError:
					self.send_error(500, "The editor template file(%s) not found. Maybe need reinstall EditOnline" % editortmplfile)
					return None
			cxt = {
				'path':self.path,
				'version':__version__,
				'realm':options.get('realm') or '',
				'exists':'true' if os.path.exists(self.translate_path(self.path.replace('~editor', ''))) else 'false',
				}
			res = EditOnlineRequestHandler.editortmpl
			for k, v in cxt.items():
				res = res.replace('{{%s}}' % k, v)

			f = StringIO()
			f.write(res)
			
			self.send_response(200)
			self.send_header("Content-type", 'text/html')
			self.send_header("Content-Length", str(f.tell()))
			self.send_header('Connection', 'close')
			self.end_headers()
			f.seek(0)
			return f
		elif os.path.isdir(path):
			parts = urlparse.urlsplit(self.path)
			if not parts.path.endswith('/'):
				# redirect browser - doing basically what apache does
				self.send_response(301)
				new_parts = (parts[0], parts[1], parts[2] + '/',
							 parts[3], parts[4])
				new_url = urlparse.urlunsplit(new_parts)
				self.send_header("Location", new_url)
				self.send_header('Connection', 'close')
				self.end_headers()
				return None
			else:
				return self.list_directory(path)
		else:
			path = self.path
			if path.startswith('/eo.static/'):
				# static
				path = os.path.join(libdir, path.replace('/eo.static/', 'static/'))
			else:
				path = self.translate_path(path)
			ctype = self.guess_type(path)
			try:
				# Always read in binary mode. Opening files in text mode may cause
				# newline translations, making the actual size of the content
				# transmitted *less* than the content-length!
				f = open(path, 'rb')
			except IOError:
				self.send_error(404, "File not found")
				return None
			try:
				self.send_response(200)
				self.send_header("Content-type", ctype)
				fs = os.fstat(f.fileno())
				self.send_header("Content-Length", str(fs[6]))
				self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
				self.send_header('Connection', 'close')
				self.end_headers()
				return f
			except:
				f.close()
				raise

	def list_directory(self, path):
		try:
			list = filter(lambda s:not s.startswith('.'), os.listdir(path))
		except os.error:
			self.send_error(404, "No permission to list directory")
			return None
		list.sort(key=lambda a: (' ' if os.path.isdir(a) else '') + a.lower())
		f = StringIO()
		displaypath = cgi.escape(urllib.unquote(self.path))
		f.write('<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">')
		f.write("<html>\n<title>Directory listing for %s</title>\n" % displaypath)
		f.write("<body>\n<h2>Directory listing for %s</h2>\n" % displaypath)
		f.write("<hr>\n<ul>\n")
		for name in list:
			fullname = os.path.join(path, name)
			displayname = linkname = name
			# Append / for directories or @ for symbolic links
			if os.path.isdir(fullname):
				displayname = name + "/"
				linkname = name + "/"
			if os.path.islink(fullname):
				displayname = name + "@"
				# Note: a link to a directory displays with @ and links with /
			isdir = os.path.isdir(fullname)
			l1 = '<a href="%s">%s</a>' % (urllib.quote(linkname), cgi.escape(displayname));
			l2 = '<a href="%s~editor" target="_blank">edit</a>' % (urllib.quote(linkname));
			if isdir:
				li = '<li>%s</li>' % l1
			else:
				li = '<li>%s [%s]</li>' % (l1, l2)
			f.write(li)
		f.write("</ul>\n<hr>\n</body>\n</html>\n")
		length = f.tell()
		f.seek(0)
		self.send_response(200)
		encoding = sys.getfilesystemencoding()
		self.send_header("Content-type", "text/html; charset=%s" % encoding)
		self.send_header("Content-Length", str(length))
		self.send_header('Connection', 'close')
		self.end_headers()
		return f

	def translate_path(self, path):
		"""Translate a /-separated PATH to the local filename syntax.

		Components that mean special things to the local file system
		(e.g. drive or directory names) are ignored.  (XXX They should
		probably be diagnosed.)

		"""
		# abandon query parameters
		path = path.split('?', 1)[0]
		path = path.split('#', 1)[0]
		# Don't forget explicit trailing slash when normalizing. Issue17324
		trailing_slash = path.rstrip().endswith('/')
		path = posixpath.normpath(urllib.unquote(path))
		words = path.split('/')
		words = filter(None, words)
		path = options.get('workdir')
		for word in words:
			drive, word = os.path.splitdrive(word)
			head, word = os.path.split(word)
			if word in (os.curdir, os.pardir): continue
			path = os.path.join(path, word)
		if trailing_slash:
			path += '/'
		return path

	def guess_type(self, path):
		"""Guess the type of a file.

		Argument is a PATH (a filename).

		Return value is a string of the form type/subtype,
		usable for a MIME Content-type header.

		The default implementation looks the file's extension
		up in the table self.extensions_map, using application/octet-stream
		as a default; however it would be permissible (if
		slow) to look inside the data to make a better guess.

		"""

		base, ext = posixpath.splitext(path)
		if ext in self.extensions_map:
			return self.extensions_map[ext]
		ext = ext.lower()
		if ext in self.extensions_map:
			return self.extensions_map[ext]
		else:
			return self.extensions_map['']

	if not mimetypes.inited:
		mimetypes.init()  # try to read system mime.types
	extensions_map = mimetypes.types_map.copy()
	extensions_map.update({
		'': 'application/octet-stream',  # Default
		'.py': 'text/plain',
		'.c': 'text/plain',
		'.h': 'text/plain',
		})

	def copyfile(self, source, outputfile):
		shutil.copyfileobj(source, outputfile)


class ThreadingHTTPServer(SocketServer.ThreadingTCPServer):
	allow_reuse_address = 1  # Seems to make sense in testing environment
	def server_bind(self):
		"""Override server_bind to store the server name."""
		SocketServer.TCPServer.server_bind(self)
		host, port = self.socket.getsockname()[:2]
		self.server_name = socket.getfqdn(host)
		self.server_port = port

def start():
	port = options['port'] if 'port' in options else 8000
	server_address = (options['bind'], port)
	httpd = ThreadingHTTPServer(server_address, EditOnlineRequestHandler)
	sa = httpd.socket.getsockname()
	print "Root Directory: %s" % options.get('workdir')
	print "Serving HTTP on", sa[0], "port", sa[1], "..."
	httpd.serve_forever()

def config(argv):
	import getopt
	opts, args = getopt.getopt(argv, "u:p:r:hd:")
	for opt, arg in opts:
		if opt == '-u':
			options['username'] = arg
		elif opt == '-p':
			options['password'] = arg
		elif opt == '-r':
			options['realm'] = arg
		elif opt == '-d':
			options['workdir'] = arg
		elif opt == '-h':
			print 'Usage: python -m EditOnline [-u username] [-p password] [-r realm] [-d workdir] [bindaddress:port | port]'
			print 'Report bugs to <sintrb@gmail.com>'
			exit()

	if options.get('username') and options.get('password'):
		import base64
		options['auth'] = base64.b64encode('%s:%s' % (options.get('username'), options.get('password')))
	if len(args) > 0:
		bp = args[0]
		if ':' in bp:
			options['bind'] = bp[0:bp.index(':')]
			options['port'] = int(bp[bp.index(':') + 1:])
		else:
			options['bind'] = '0.0.0.0'
			options['port'] = int(bp)

def main():
	config(sys.argv[1:])
	start()
	
if __name__ == '__main__':
	main()
