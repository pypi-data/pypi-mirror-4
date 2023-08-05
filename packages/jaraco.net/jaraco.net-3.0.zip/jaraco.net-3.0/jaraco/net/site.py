from __future__ import print_function

import argparse

from path import path
from jaraco.util.string import local_format as lf

def make_index_cmd():
	"""
	Generate an index file for each directory that itself has an
	index.htm file
	"""
	parser = argparse.ArgumentParser()
	parser.add_argument('root', default=path('.'), type=path)
	args = parser.parse_args()
	print('<ul>')
	for dir in sorted(args.root.dirs()):
		if not (
			(dir/'index.htm').exists() or
			(dir/'index.html').exists()): continue
		dir = dir.basename()
		print(lf('<li><a href="{dir}/index.htm">{dir}</a></li>'))
	print('</ul>')
