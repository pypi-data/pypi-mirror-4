# -*- coding: UTF-8 -*-

"""
Setup script for building jaraco.net

Copyright © 2009-2011 Jason R. Coombs
"""

import sys

from setuptools import find_packages

name = 'jaraco.net'

py26reqs = ['argparse'] if sys.version_info < (2, 7) else []

windows_scripts = [
	'whois-bridge-service = jaraco.net.whois:Service.handle_command_line',
	'wget = jaraco.net.http:wget',
	] if sys.platform == 'win32' else []

setup_params = dict(
	name = name,
	use_hg_version=dict(increment='0.0.1'),
	description = 'Networking tools by jaraco',
	long_description = open('README').read(),
	author = 'Jason R. Coombs',
	author_email = 'jaraco@jaraco.com',
	url = 'http://bitbucket.org/jaraco/' + name,
	packages = find_packages(),
	namespace_packages = ['jaraco'],
	license = 'MIT',
	classifiers = [
		"Development Status :: 5 - Production/Stable",
		"Intended Audience :: Developers",
		"Programming Language :: Python",
	],
	entry_points = {
		'console_scripts': [
			'whois-bridge = jaraco.net.whois:serve',
			'scanner = jaraco.net.scanner:scan',
			'fake-http = jaraco.net.http.servers:Simple.start',
			'fake-http-auth = jaraco.net.http.servers:AuthRequest.start',
			'serve-local = jaraco.net.http.static:serve_local',
			'fake-smtp = jaraco.net.smtp:start_simple_server',
			'udp-send = jaraco.net.udp:Sender',
			'udp-echo = jaraco.net.udp:EchoServer',
			'dns-forward-service = jaraco.net.dns:ForwardingService.handle_command_line',
			'dnsbl-check = jaraco.net.dnsbl:Service.handle_command_line',
			'ntp = jaraco.net.ntp:handle_command_line',
			'remove-known-spammers = jaraco.net.email:remove_known_spammers',
			'tcp-test-connect = jaraco.net.tcp:test_connect',
			'tcp-echo-server = jaraco.net.tcp:start_echo_server',
			'http-headers = jaraco.net.http:headers',
			'build-dir-index = jaraco.net.site:make_index_cmd',
			'content-type-reporter = jaraco.net.http.content:ContentTypeReporter.run',
			'web-tail = jaraco.net.tail:handle_command_line',
			'rss-launch = jaraco.net.rss:launch_feed_enclosure',
			'rss-download = jaraco.net.rss:download_enclosures',
		] + windows_scripts,
	},
	install_requires=[
		'jaraco.util>=5.0',
		'clientform>=0.2.7',
		'BeautifulSoup',
		'keyring>=0.6',
		'feedparser',
	] + py26reqs,
	extras_require = {
	},
	dependency_links = [
	],
	tests_require=[
	],
	setup_requires = [
		'hgtools>=0.6.4',
	],
	use_2to3=True,
)

if __name__ == '__main__':
	from setuptools import setup
	setup(**setup_params)
