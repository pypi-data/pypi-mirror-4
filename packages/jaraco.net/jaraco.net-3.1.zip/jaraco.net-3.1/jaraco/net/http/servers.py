from __future__ import print_function

import socket
import sys
import re
import time
import datetime
import argparse
import functools

from jaraco.util.string import local_format as lf

class Simple(object):
	def __init__(self, host, port, timeout, response_delay, outfile):
		self.__dict__.update(vars())
		del self.self

	@classmethod
	def start(cls):
		options = cls.get_args()
		server = cls(**vars(options))
		server.serve()

	@staticmethod
	def get_args():
		p = argparse.ArgumentParser(conflict_handler="resolve")
		p.add_argument('-h', '--host', help="Bind to IP address", default='')
		p.add_argument('-p', '--port', type=int, help="Bind to port",
			default=80)
		p.add_argument('-t', '--timeout', type=int, help="Socket timeout",
			default=3)
		p.add_argument('-o', '--outfile', default=sys.stdout,
			type=functools.partial(open, mode='wb'), help='save output to file',
		)
		seconds = lambda seconds: datetime.timedelta(seconds=seconds)
		p.add_argument('-d', '--delay', dest='response_delay', type=seconds,
			help="Artificial delay in response", default=datetime.timedelta())
		return p.parse_args()

	def serve_one(self):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.bind((self.host, self.port))
		s.listen(1)
		self.conn, addr = s.accept()
		print('Accepted connection from', addr)
		self.get_response()
	serve = serve_one

	def get_response(self):
		try:
			self.conn.settimeout(self.timeout)
			headers, content = self.get_headers(self.conn)
			content_len = self.get_content_length(headers) or 0
			content = self.get_content(self.conn, content, content_len)
			self.conn.send('HTTP/1.0 200 OK\r\n')
			time.sleep(self.response_delay.total_seconds())
			self.conn.send('\r\nGot It!')
		except socket.error, e:
			print('Error %s' % e)
			if content:
				print('partial result')
				print(repr(content), file=self.outfile)
		finally:
			self.conn.close()

	@staticmethod
	def get_content_length(request):
		match = re.search('^Content-Length:\s+(\d+)\s*$', request, re.I | re.MULTILINE)
		if match:
			return int(match.group(1))
		print('no content length found', file=sys.stderr)

	@staticmethod
	def get_headers(conn):
		res = ''
		while not '\r\n\r\n' in res:
			res += conn.recv(1024)
		bytes = len(res)
		headers, _sep, content = res.partition('\r\n\r\n')
		print('received %(bytes)d bytes' % vars(), file=sys.stderr)
		print(headers)
		return headers, content

	def get_content(self, conn, content='', length=0):
		while len(content) < length:
			content += conn.recv(1024)
		bytes = len(content)
		print('received %(bytes)d bytes content' % vars(), file=sys.stderr)
		print(content, file=self.outfile)
		return content


class AuthRequest(Simple):
	def serve_until_auth(self):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.bind((self.host, self.port))
		s.listen(1)
		while True:
			self.conn, addr = s.accept()
			print(lf('Accepted connection from {addr}'))

			if not self.check_auth_response(self.conn) == 'retry': break
	serve = serve_until_auth

	def check_auth_response(self, conn):
		try:
			conn.settimeout(self.timeout)
			headers, content = self.get_headers(conn)
			content_len = self.get_content_length(headers) or 0
			content = self.get_content(self.conn, content, content_len)
			user_pat = re.compile('^Authorization:\s+(.*)\s*$', re.I|re.MULTILINE)
			matched_header = user_pat.search(headers)
			if matched_header:
				conn.send('HTTP/1.0 200 OK\r\n')
				user = matched_header.group(1)
				conn.send('\r\nYou are authenticated as %(user)s' % vars())
				return
			conn.send('HTTP/1.0 401 Authorization Required\r\n')
			conn.send('Connection: close\r\n')
			msg = 'Go get me some credentials'
			conn.send('Content-Length: %d\r\n' % len(msg))
			conn.send('WWW-Authenticate: NTLM\r\n')
			conn.send('WWW-Authenticate: Basic realm="fake-auth"\r\n')
			conn.send('\r\n')
			conn.send(msg)
			print('sent authorization request')
		except socket.error, e:
			print('error in connection')
			traceback.print_exc()
			if res:
				print('partial result')
				print(repr(res))
		finally:
			conn.close()
		return 'retry'
