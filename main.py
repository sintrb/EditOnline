# -*- coding: UTF-8 -*
'''
@author: sintrb
'''
"""Simple HTTP Server.

This module builds on BaseHTTPServer by implementing the standard GET
and HEAD requests in a fairly straightforward manner.

"""


__version__ = "0.1"

import os
import posixpath
import BaseHTTPServer
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

class EditOnlineRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
	server_version = "EditOnline/" + __version__
	def do_GET(self):
		f = self.send_head()
		if f:
			try:
				self.copyfile(f, self.wfile)
			finally:
				f.close()

	def do_POST(self):
		self.path = self.path.replace('..', '')

		length = int(self.headers.getheader('content-length'))
		body = self.rfile.read(length)
		path = self.translate_path(self.path).replace('~editor','')
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
			try:
				res = ''.join(open(os.path.join(libdir, 'editor.html')).readlines())
				cxt = {
					'path':self.path,
					'version':__version__,
					'exists':'true' if os.path.exists(self.translate_path(self.path.replace('~editor',''))) else 'false',
					}
				
				for k, v in cxt.items():
					res = res.replace('{{%s}}' % k, v)

				f = StringIO()
				f.write(res)
				
				self.send_response(200)
				self.send_header("Content-type", 'text/html')
				self.send_header("Content-Length", str(f.tell()))
				self.end_headers()
				f.seek(0)
				return f
			except IOError:
				self.send_error(404, "File not found")
				return None
		elif os.path.isdir(path):
			parts = urlparse.urlsplit(self.path)
			if not parts.path.endswith('/'):
				# redirect browser - doing basically what apache does
				self.send_response(301)
				new_parts = (parts[0], parts[1], parts[2] + '/',
							 parts[3], parts[4])
				new_url = urlparse.urlunsplit(new_parts)
				self.send_header("Location", new_url)
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
			f.write('<li><a href="%s"%s>%s</a>\n'
					% (urllib.quote(linkname) + ('' if isdir else '~editor'), '' if isdir else ' target="_blank"', cgi.escape(displayname)))
		f.write("</ul>\n<hr>\n</body>\n</html>\n")
		length = f.tell()
		f.seek(0)
		self.send_response(200)
		encoding = sys.getfilesystemencoding()
		self.send_header("Content-type", "text/html; charset=%s" % encoding)
		self.send_header("Content-Length", str(length))
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
		path = os.getcwd()
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

def test(HandlerClass=EditOnlineRequestHandler, ServerClass=BaseHTTPServer.HTTPServer):
	BaseHTTPServer.test(HandlerClass, ServerClass)

if __name__ == '__main__':
	test()




