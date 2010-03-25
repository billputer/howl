"""
simple_http_test.py

simple test for debugging
"""

import unittest, simplejson

from test_utils import WebCase, print_timing

class TestSimple(WebCase):
	"""Simple test for debugging purposes"""
	
	def testSimple(self):
		"""Sends an HTTP request to 'player/status/'"""
		
		self.getPage("player/status/", method = "GET")
		self.assertStatus(status = 200)
		
		print 'http headers:'
		for header in self.headers.items():
			print header
		print 'body:'
		print simplejson.dumps(self.body,indent=1)\

if __name__ == '__main__':
	unittest.main()



