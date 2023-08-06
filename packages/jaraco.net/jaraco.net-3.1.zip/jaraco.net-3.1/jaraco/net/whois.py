#! -*- coding: UTF-8 -*-

"""whois_bridge.py

HTTP scraper for nic servers who only offer whois service via web only.

Run the script from the command line and it will service port 43 as a whois
server, passing the query to the appropriate web form and parsing the results
into a textual format.

Copyright © 2005-2011 Jason R. Coombs
"""

import os
import re
import sys
import logging
import htmllib
import abc
import formatter
import urllib
import urllib2
import cookielib
import socket
import select
import SocketServer

import jaraco.util.logging
from ClientForm import ParseResponse, ItemNotFoundError
from BeautifulSoup import BeautifulSoup, UnicodeDammit
from jaraco.util.meta import LeafClassesMeta

try:
	import win32service
	import win32serviceutil
	import servicemanager
except ImportError:
	pass

from .http import PageGetter

log = logging.getLogger(__name__)

def init():
	"""
	Initialize HTTP functionality to support cookies, which are necessary
	to use the HTTP interface.
	"""
	cj = cookielib.CookieJar()
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
	urllib2.install_opener(opener)

class WhoisHandler(object):
	"""
	WhoisHandler is an abstract class for defining whois interfaces for
	web-based nic servers.
	"""

	__metaclass__ = LeafClassesMeta

	@abc.abstractproperty
	def services(self):
		"Regular expression that will match domains serviced by this handler."

	@abc.abstractmethod
	def LoadHTTP(self):
		"""
		Retrieve the HTTP response and a _parser class which is an HTMLParser
		capable of parsing the response and outputting the textual result.
		"""

	def __init__(self, query = None):
		self._query = query

	@classmethod
	def _query_matches_services(cls, query):
		return re.search(cls.services, query, re.IGNORECASE)

	@staticmethod
	def GetHandler(query):
		"""Search through the WhoisHandler subclasses and return the one
		that matches the query."""
		query = query.lower()
		handlers = WhoisHandler._leaf_classes
		matches = [c for c in handlers if c._query_matches_services(query)]
		if not len(matches) == 1:
			error = [
				'Domain for %s is not serviced by this server.',
				'Server error, ambiguous nic server resolution for %s.',
				][bool(len(matches))]
			raise ValueError(error % query)
		return matches[0](query)

	def _IsWhoisHandler_(ob):
		return hasattr(ob, '__bases__') and WhoisHandler in ob.__bases__
	_IsWhoisHandler_ = staticmethod(_IsWhoisHandler_)

	def ParseResponse(self, s_out):
		# fix the response; the parser doesn't understand tags that have a slash
		# immediately following the tag name (part of the XHTML 1.0 spec).
		# Alternatively, one could use tidylib with 'drop-empty-paras' set to False
		# response = str(tidy.parseString(response, drop_empty_paras = False))
		response = re.sub(r'<(\w+)/>', r'<\1 />', self._response)
		writer = MyWriter(s_out)
		self._parser(formatter.AbstractFormatter(writer)).feed(response)

class ArgentinaWhoisHandler(WhoisHandler):
	services = r'\.ar$'

	def LoadHTTP(self):
		query = self._query
		pageURL = 'http://www.nic.ar/consdom.html'
		form = ParseResponse(urllib2.urlopen(pageURL))[0]
		form['nombre'] = query[:query.find('.')]
		try:
			domain = query[query.find('.'):]
			form['dominio'] = [domain]
		except ItemNotFoundError:
			raise ValueError('Invalid domain (%s)' % domain)
		req = form.click()
		#req.data = 'nombre=%s&dominio=.com.ar' % query
		req.add_header('referer', pageURL)
		resp = urllib2.urlopen(req)
		self._response = resp.read()

	class _parser(htmllib.HTMLParser):
		def start_tr(self, attrs):
			"One must define start_tr for end_tr to be called."

		def end_tr(self):
			self.formatter.add_line_break()

class CoZaWhoisHandler(WhoisHandler):
	services = r'\.co\.za$'

	def LoadHTTP(self):
		query = self._query
		pageURL = 'http://whois.co.za/'
		form = ParseResponse(urllib2.urlopen(pageURL))[0]
		form['Domain'] = query[:query.find('.')]
		req = form.click()
		resp = urllib2.urlopen(req)
		self._response = resp.read()

	_parser = htmllib.HTMLParser

class GovWhoisHandler(WhoisHandler):
	services = r'(\.fed\.us|\.gov)$'

	def LoadHTTP(self):
		query = self._query
		# Perform an whois query on the dotgov server.
		url = urllib2.urlopen('http://dotgov.gov/whois.aspx')
		forms = ParseResponse(url)
		assert len(forms) == 1
		form = forms[0]
		if form.attrs['action'] == 'agree.aspx':
			# we've been redirected to a different form
			# need to agree to license agreement
			self.Agree(form)
			# note this could get to an infinite loop if cookies aren't working
			# or for whatever reason we're always being redirected to the
			# agree.aspx page.
			return self.LoadHTTP()
		form['who_search'] = query
		resp = urllib2.urlopen(forms[0].click())
		self._response = resp.read()

	def Agree(self, form):
		"agree to the dotgov agreement"
		agree_req = form.click()
		u2 = urllib2.urlopen(agree_req)
		u2.read()

	class _parser(htmllib.HTMLParser):
		def __init__(self, formatter):
			self.__formatter__ = formatter
			# Use the null formatter to start; we'll switch to the outputting
			#  formatter when we find the right point in the HTML.
			htmllib.HTMLParser.__init__(self, formatter.NullFormatter())

		def start_td(self, attrs):
			attrs = dict(attrs)
			# I identify the important content by the tag with the ID 'TD1'.
			# When this tag is found, switch the formatter to begin outputting
			#  the response.
			if 'id' in attrs and attrs['id'] == 'TD1':
				self.formatter = self.__formatter__

		def end_td(self):
			# switch back to the NullFormatter
			if not isinstance(self.formatter, formatter.NullFormatter):
				self.formatter = formatter.NullFormatter()

mozilla_headers = {
	'referer': 'http://www.nic.bo/buscar.php',
	'accept': 'text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5',
	'accept-encoding': 'gzip,deflate',
	'user-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8) Gecko/20051111 Firefox/1.5',
	'accept-charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
	'accept-language': 'en-us,en;q=0.5',
}

class BoliviaPageGetter(PageGetter):
	url = 'http://www.nic.bo/'
#	def GetRequest(self):
#		request = super(self.__class__, self).GetRequest()
#		map(request.add_header, mozilla_headers.keys(), mozilla_headers.values())
#		return request

class BoliviaWhoisHandler(WhoisHandler):
	services = r'\.bo$'

	class _parser(htmllib.HTMLParser):
		def anchor_end(self):
			if self.anchor:
				self.handle_data('[%s]' % self.anchor)
				self.anchor = None

	def LoadHTTP(self):
		name, domain = self._query.split('.', 1)
		domain = '.' + domain
		getter = BoliviaPageGetter()
		getter.form_items = {'subdominio': [domain], 'dominio': name}
		getter.request = getter.Process()
		self._response = getter.Fetch().read()
		del getter.request

		# now that we've submitted the request, we've got a response.
		# Unfortunately, this page returns 'available' or 'not available'
		# If it's not available, we need to know who owns it.
		if re.search('Dominio %s registrado' % self._query, self._response):
			getter.url = urllib.basejoin(getter.url, 'informacion.php')
			self._response = getter.Fetch().read()

	def ParseResponse(self, s_out):
		soup = BeautifulSoup(self._response)
		#self._response = unicode(soup.strong.parent.div).encode('latin-1')
		self._response = unicode(soup.strong.parent.div)
		return super(self.__class__, self).ParseResponse(s_out)

class SourceWhoisHandler(WhoisHandler):
	"""This is not a typical Whois handler, but rather a special
	handler that returns the source of this file"""
	services = r'^source$'

	def LoadHTTP(self): pass

	def ParseResponse(self, s_out):
		filename = os.path.splitext(__file__)[0] + '.py'
		s_out.write(open(filename).read())

class DebugHandler(WhoisHandler):
	services = r'^debug (.*)$'
	authorized_addresses = ['127.0.0.1']

	def LoadHTTP(self): pass

	def ParseResponse(self, s_out):
		if self.client_address[0] in self.authorized_addresses:
			match = re.match(self.services, self._query)
			s_out.write('result: %s' % eval(match.group(1)))

# disable the debug handler
del DebugHandler

class MyWriter(formatter.DumbWriter):
	def send_flowing_data(self, data):
		data = UnicodeDammit(data).unicode
		# convert non-breaking spaces to regular spaces
		data = data.replace(u'\xa0', u' ')
		formatter.DumbWriter.send_flowing_data(self, data)

class Handler(SocketServer.StreamRequestHandler):
	def handle(self):
		try:
			self._handle()
		except:
			log.exception('unhandled exception')

	def _handle(self):
		query = self.rfile.readline().strip()
		log.info('%s requests %s', self.client_address, query)
		try:
			handler = WhoisHandler.GetHandler(query)
			handler.client_address = self.client_address
			handler.LoadHTTP()
			handler.ParseResponse(self.wfile)
			log.info('%s success', self.client_address)
		except urllib2.URLError:
			msg = 'Could not contact whois HTTP service.'
			self.wfile.write(msg + '\n')
			log.exception(msg)
		except ValueError, e:
			log.info('%s response %s', self.client_address, e)
			self.wfile.write('%s\n' % e)

class ConnectionClosed(Exception): pass

class Listener(SocketServer.ThreadingTCPServer):
	def __init__(self):
		SocketServer.ThreadingTCPServer.__init__(self, ('', 43), Handler)

	def serve_until_closed(self):
		try:
			while True: self.handle_request()
		except ConnectionClosed:
			pass

	def get_request(self):
		# use select here because select will throw an exception if the socket
		#  is closed.  Simply blocking on accept will block even if the socket
		#  object is closed.
		try:
			select.select((self.socket,), (), ())
		except socket.error, e:
			if e[1].lower() == 'bad file descriptor':
				raise ConnectionClosed
		return SocketServer.ThreadingTCPServer.get_request(self)

def serve():
	init()
	l = Listener()
	l.serve_forever()

# On Windows, run as a service
if 'win32serviceutil' in globals():
	class Service(win32serviceutil.ServiceFramework):
		_svc_name_ = 'whois_bridge'
		_svc_display_name_ = 'Whois HTTP Bridge'

		def __init__(self, args):
			win32serviceutil.ServiceFramework.__init__(self, args)

		def SvcStop(self):
			self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
			self.listener.server_close()

		def SvcDoRun(self):
			self._setup_logging()

			log.info('%s service is starting.', self._svc_display_name_)
			servicemanager.LogMsg(
				servicemanager.EVENTLOG_INFORMATION_TYPE,
				servicemanager.PYS_SERVICE_STARTED,
				(self._svc_name_, '')
				)

			self.run()

			servicemanager.LogMsg(
				servicemanager.EVENTLOG_INFORMATION_TYPE,
				servicemanager.PYS_SERVICE_STOPPED,
				(self._svc_name_, '')
				)
			log.info('%s service is stopped.', self._svc_display_name_)

		def run(self):
			init()
			self.listener = Listener()
			self.listener.serve_until_closed()

		def _setup_logging(self):
			logfile = os.path.join(os.environ['WINDIR'], 'system32', 'LogFiles', self._svc_display_name_, 'events.log')
			handler = jaraco.util.logging.TimestampFileHandler(logfile)
			handlerFormat = '[%(asctime)s] - %(levelname)s - [%(name)s] %(message)s'
			handler.setFormatter(logging.Formatter(handlerFormat))
			logging.root.addHandler(handler)
			# if I don't redirect stdoutput and stderr, when the stdio flushes,
			#  an exception will be thrown and the service will bail
			sys.stdout = jaraco.util.logging.LogFileWrapper('stdout')
			sys.stderr = jaraco.util.logging.LogFileWrapper('stderr')
			logging.root.level = logging.INFO

		@classmethod
		def handle_command_line(cls):
			win32serviceutil.HandleCommandLine(cls)

if __name__ == '__main__':
	serve()
