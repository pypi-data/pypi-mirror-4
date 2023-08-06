#!python

import os
test_dir = os.path.dirname(__file__)

def test_bolivia_handler():
	from jaraco.net.whois import BoliviaWhoisHandler
	import StringIO
	handler = BoliviaWhoisHandler('microsoft.com.bo')
	handler.client_address = '127.0.0.1'
	test_result = os.path.join(test_dir, 'nic.bo.html')
	handler._response = open(test_result).read()
	result = StringIO.StringIO()
	handler.ParseResponse(result)
	assert 'Microsoft Corporation' in result.getvalue()