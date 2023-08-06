from __future__ import print_function

"""
HTTP routines
"""

import logging
import os
import re
import datetime
import argparse
import urlparse
import urllib
import urllib2
import httplib
import cgi
import ClientForm
import cookielib

import jaraco.util.string
from jaraco.filesystem import set_time

log = logging.getLogger(__name__)


class Query(dict):
	"""HTTP Query takes as an argument an HTTP query request
	(from the url after ?) or a URL and maps all of the query pairs
	in itself as a dictionary.
	>>> Query('a=b&c=3&4=20') == {'a':'b', 'c':'3', '4':'20'}
	True
	>>> Query('http://www.jaraco.com/?test=30') == {'test':'30'}
	True
	>>> Query('http://www.jaraco.com/') == {}
	True
	>>> Query('') == {}
	True
	"""
	def __init__(self, query):
		query = Query.__QueryFromURL__(query) or query
		if not re.match(r'(\w+=\w+(&\w+=\w+)*)*$', query): query = ()
		if isinstance(query, basestring):
			items = query.split('&')
			# remove any empty values
			items = filter(None, items)
			itemPairs = map(jaraco.util.string.Splitter('='), items)
			unquoteSequence = lambda l: map(urllib.unquote, l)
			query = map(unquoteSequence, itemPairs)
		if isinstance(query, (tuple, list)):
			query = dict(query)
		if not isinstance(query, dict):
			msg = "Can't construct a %s from %s"
			raise ValueError(msg % (self.__class__, query))
		self.update(query)

	def __repr__(self):
		return urllib.urlencode(self)

	@staticmethod
	def __QueryFromURL__(url):
		"Return the query portion of a URL"
		return urlparse.urlparse(url).query

class PageGetter(object):
	"""
	PageGetter
	A helper class for common HTTP page retrieval.
	"""

	_opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.CookieJar()))

	def __init__(self, **attrs):
		"set url to the target url or set request to the urllib2.Request object"
		self.__dict__.update(attrs)

	def GetRequest(self):
		req = getattr(self, 'request', None) or urllib2.Request(getattr(self, 'url'))
		return req

	def Fetch(self):
		return self._opener.open(self.GetRequest())

	def Process(self):
		resp = self.Fetch()
		forms = ClientForm.ParseResponse(resp)
		form = self.SelectForm(forms)
		self.FillForm(form)
		return form.click()

	def SelectForm(self, forms):
		sel = getattr(self, 'form_selector', 0)
		log.info('selecting form %s', sel)
		if not isinstance(sel, int):
			# assume the selector is the name of the form
			forms = dict(map(lambda f: (f.name, f), forms))
		return forms[sel]

	def FillForm(self, form):
		for name, value in self.form_items.items():
			if callable(value):
				value = value()
			form[name] = value

	def __call__(self, next):
		# process the form and set the request for the next object
		next.request = self.Process()
		return next

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

class HeadRequest(MethodRequest):
	method = 'HEAD'

def get_content_disposition_filename(url):
	"""
	Get the content disposition filename from a URL.
	Returns None if no such disposition can be found.

	If `url` is already an addinfourl object, it will use its headers.
	Otherwise, urllib2 is used to retrieve the headers.

	>>> url = 'http://www.voidspace.org.uk/cgi-bin/voidspace/downman.py?file=pythonutils-0.3.0.zip'
	>>> get_content_disposition_filename(url) in (None, 'pythonutils-0.3.0.zip')
	True

	>>> url = 'http://www.example.com/invalid_url'
	>>> get_content_disposition_filename(url) is None
	True

	>>> url = 'http://www.google.com/'
	>>> get_content_disposition_filename(url) is None
	True

	"""

	res = url
	if not isinstance(url, urllib2.addinfourl):
		req = HeadRequest(url)
		try:
			res = urllib2.urlopen(req)
		except urllib2.URLError:
			return
	header = res.headers.get('content-disposition', '')
	value, params = cgi.parse_header(header)
	return params.get('filename')

def get_url_filename(url):
	return os.path.basename(urlparse.urlparse(url).path)

def get_url(url, dest=None, replace_newer=False, touch_older=True):
	src = urllib2.urlopen(url)
	log.debug(src.headers)
	if 'last-modified' in src.headers:
		mod_time = datetime.datetime.strptime(src.headers['last-modified'], '%a, %d %b %Y %H:%M:%S %Z')
	else:
		mod_time = None
	content_length = int(src.headers['content-length'])
	fname = dest or get_content_disposition_filename(src) or get_url_filename(url) or 'result.dat'
	if mod_time and os.path.exists(fname):
		stat = os.lstat(fname)
		previous_size = stat.st_size
		previous_mod_time = datetime.datetime.utcfromtimestamp(stat.st_mtime)
		log.debug('Local  last mod %s', previous_mod_time)
		log.debug('Remote last mod %s', mod_time)
		log.debug('Local  size %d', previous_size)
		log.debug('Remote size %d', content_length)
		if not replace_newer and not touch_older: raise RuntimeError, "%s exists" % fname
		if replace_newer and previous_mod_time >= mod_time and previous_size == content_length:
			log.info('File is current')
			return
		just_needs_touching = touch_older and previous_mod_time > mod_time and previous_size == content_length
		if just_needs_touching:
			log.info('Local file appears newer than remote - updating mod time')
			set_time(fname, mod_time)
			return
	log.info('Downloading %s (last mod %s)', url, str(mod_time))
	dest = open(fname, 'wb')
	for line in src:
		dest.write(line)
	dest.close()
	if mod_time:
		set_time(fname, mod_time)
	return fname

def print_headers(url):
	parsed = urlparse.urlparse(url)
	conn_class = dict(
		http=httplib.HTTPConnection,
		https=httplib.HTTPSConnection,
		)
	conn = conn_class[parsed.scheme](parsed.netloc)
	selector = parsed.path or '/'
	if parsed.query: selector += '?' + parsed.query
	conn.request('HEAD', selector)
	response = conn.getresponse()
	if response.status == 200:
		print(response.msg)

def _get_url_from_command_line():
	parser = argparse.ArgumentParser()
	parser.add_argument('url')
	args = parser.parse_args()
	return args.url

def wget():
	get_url(_get_url_from_command_line())

def headers():
	print_headers(_get_url_from_command_line())
