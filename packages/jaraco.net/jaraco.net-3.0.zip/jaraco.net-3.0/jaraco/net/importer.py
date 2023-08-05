import types
import urllib2
import sys
import logging
import urlparse

# python 3 compatibility
exec(
	"def do_exec(co, loc): exec(co, loc)\n"
	if sys.version_info >= (3,) else
	"def do_exec(co, loc): exec co in loc\n"
)

log = logging.getLogger(__name__)

class HeadRequest(urllib2.Request):
	def get_method(self): return 'HEAD'

class URLLoader(str):
	def load_module(self, fullname):
		url = self + fullname + '.py'
		resp = urllib2.urlopen(url)
		co = compile(resp.read(), fullname, 'exec')
		module = sys.modules.setdefault(fullname, types.ModuleType(fullname))
		module.__file__ = url
		module.__loader__ = self
		do_exec(co, module.__dict__)
		return sys.modules[fullname]

class URLImporter(str):
	"""
	Simple Importer that imports from the network
	"""
	# interface.Provides(python_importer)

	def find_module(self, fullname, path=None):
		log.debug("Finding %s in %s", fullname, self)
		if not self.endswith('/'):
			return
		req = HeadRequest(self+fullname+'.py')
		try:
			resp = urllib2.urlopen(req)
			log.debug("Found at %s", self)
			return URLLoader(self)
		except Exception:
			pass

	@classmethod
	def install(cls):
		sys.path_hooks.append(cls.handles)

	@classmethod
	def remove(cls):
		sys.path_hooks.remove(cls.handles)

	@classmethod
	def handles(cls, path):
		path_p = urlparse.urlparse(path)
		if path_p.scheme in ('http', 'https'):
			return cls(path)
		raise ImportError(path)
