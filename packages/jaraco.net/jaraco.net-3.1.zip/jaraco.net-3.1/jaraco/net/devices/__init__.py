import sys
try:
	__mod = __import__(__name__+'.'+sys.platform, fromlist=['Manager'])
	Manager = __mod.Manager
except ImportError:
	from base import BaseManager as Manager
