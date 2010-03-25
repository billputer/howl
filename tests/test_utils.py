"""
test_utils.py

adds WebCase for testing Howl server functionality
"""

import sys, time,socket
import unittest
import commands
import pprint

import simplejson
import httplib2
import howl

class WebCase(unittest.TestCase):
	"""
	Modification of the CherryPy WebCase tests.
	
	Defines the self.getPage method to request a page from Howl
	"""
	def __init__(self,*args):
		unittest.TestCase.__init__(self,*args)
		self.HOST = 'localhost'
		self.PORT = howl.config.port
		self.username = "test_user"
		self.password = "test"
		self.request_headers = {'Content-Type':'application/json',
						'Accept':'application/json'}
		self.client = httplib2.Http()
		self.client.add_credentials(self.username,self.password)
		self.client.follow_redirects = True
	
	def getPage(self, uri, headers={}, method="GET", body=None, convert_body=True):
		"""Open the uri with debugging support. Return status, headers, body."""
		if not uri.startswith("http"):
			self.uri = "http://%s:%s/%s"% (self.HOST,self.PORT,uri)
		else:
			self.uri = uri
		
		headers.update(self.request_headers)
		if body and not type(body) == str:
			body = simplejson.dumps(body)
		# Trying 10 times is simply in case of socket errors.
		# Normal case--it should run once.
		result = None
		for trial in xrange(10):
			try:
				result = self.client.request(self.uri,method,body=body,headers=headers)
				break
			except socket.error:
				time.sleep(0.5)
		
		try:
			self.headers, self.body = result
		except TypeError:
			self._handlewebError('Unable to reach server')
		
		self.status = self.headers['status']
		if self.body and convert_body:
			try:
				self.body = simplejson.loads(self.body)
			except:
				self._handlewebError(self._exc_info()[1])
	
	
	interactive = True
	console_height = 30
	
	def _handlewebError(self, msg):
		print
		print "ERROR:", msg
		
		if not self.interactive:
			raise self.failureException(msg)
		
		p = "Show: [B]ody [H]eaders [S]tatus [U]RI; [I]gnore, [R]aise, or sys.e[X]it >> "
		print p,
		while True:
			i = getchar().upper()
			if i not in "BHSUIRX":
				continue
			print i.upper()	 # Also prints new line
			if i == "B":
				pretty_print_error(self.body)
			elif i == "H":
				pprint.pprint(self.headers)
			elif i == "S":
				print self.status
			elif i == "U":
				print self.uri
			elif i == "I":
				# return without raising the normal exception
				return
			elif i == "R":
				raise self.failureException(msg)
			elif i == "X":
				self.exit()
			print p,
	
	def exit(self):
		sys.exit()
	
	def __call__(self, result=None):
		if result is None:
			result = self.defaultTestResult()
		result.startTest(self)
		testMethod = getattr(self, self._testMethodName)
		try:
			try:
				self.setUp()
			except (KeyboardInterrupt, SystemExit):
				raise
			except:
				result.addError(self, self._exc_info())
				return
			
			ok = 0
			try:
				testMethod()
				ok = 1
			except self.failureException:
				result.addFailure(self, self._exc_info())
			except (KeyboardInterrupt, SystemExit):
				raise
			except:
				result.addError(self, self._exc_info())
			
			try:
				self.tearDown()
			except (KeyboardInterrupt, SystemExit):
				raise
			except:
				result.addError(self, self._exc_info())
				ok = 0
			if ok:
				result.addSuccess(self)
		finally:
			result.stopTest(self)
	
	def assertStatus(self, status, msg=None):
		"""Fail if self.status != status."""
		if isinstance(status, basestring):
			if not self.status == status:
				if msg is None:
					msg = 'Status (%s) != %s' % (`self.status`, `status`)
				self._handlewebError(msg)
		elif isinstance(status, int):
			code = int(self.status[:3])
			if code != status:
				if msg is None:
					msg = 'Status (%s) != %s' % (`self.status`, `status`)
				self._handlewebError(msg)
	
	def assertHeader(self, key, value=None, msg=None):
		"""Fail if (key, [value]) not in self.headers."""
		lowkey = key.lower()
		for k, v in self.headers.iteritems():
			if k.lower() == lowkey:
				if value is None or str(value) == v:
					return v
		
		if msg is None:
			if value is None:
				msg = '%s not in headers' % `key`
			else:
				msg = '%s:%s not in headers' % (`key`, `value`)
		self._handlewebError(msg)
	
	def assertNoHeader(self, key, msg=None):
		"""Fail if key in self.headers."""
		lowkey = key.lower()
		matches = [k for k, v in self.headers.iteritems() if k.lower() == lowkey]
		if matches:
			if msg is None:
				msg = '%s in headers' % `key`
			self._handlewebError(msg)
	
	def assertValidBody(self, json_type, msg=None):
		"""Fail if self.body is not valid json"""
		try:
			simplejson.dumps(self.body)
		
		except:
			if msg is None:
				msg = format_exc()
			self._handlewebError(msg)
		try:
			self.assert_(self.body.keys()[0] == json_type)
		except:
			if msg is None:
				msg = "Body is not of type '%s'" % json_type
			self._handlewebError(msg)
	
	def assertResponse(self,status,body_type):
		self.assertStatus(status)
		self.assertValidBody(body_type)


def format_exc(exc=None):
	"""Return exc (or sys.exc_info if None), formatted."""
	if exc is None:
		exc = sys.exc_info()
	if exc == (None, None, None):
		return ""
	import traceback
	return "".join(traceback.format_exception(*exc))

def pretty_print_error(error):
	if type(error) == dict:
		print "{'error':"
		print "{'status': 500,"
		print "'message':"
		print error['error']['message']
		if error.has_key('traceback'):
			print "'traceback':"
			print error['error']['traceback']
		print "}"
	else:
		pprint.pprint(error)

try:
	# On Windows, msvcrt.getch reads a single char without output.
	import msvcrt
	def getchar():
		return msvcrt.getch()
except ImportError:
	# Unix getchr
	import tty, termios
	def getchar():
		fd = sys.stdin.fileno()
		old_settings = termios.tcgetattr(fd)
		try:
			tty.setraw(sys.stdin.fileno())
			ch = sys.stdin.read(1)
		finally:
			termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
		return ch

def print_timing(func):
	def wrapper(*arg):
		t1 = time.time()
		res = func(*arg)
		t2 = time.time()
		print '%s took %0.3f ms' % (func.func_name, (t2-t1)*1000.0)
		return res
	return wrapper