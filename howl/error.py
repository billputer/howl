"""
error.py

Drop-in replacement for CherryPy error handling.
Internal Error, etc, all return JSON instead of HTML.
"""

import cherrypy
import simplejson
import sys

class InternalError(Exception):
	"""
	Class defined to override default cherrypy error handler.
	Error responses are defined in JSON.
	"""
	def __init__(self, status = 500, message=None):
		self.status = status = int(status)
		if status < 399 or status > 599:
			raise ValueError("status must be between 400 and 599.")
		if not message:
			self.message = "An unknown error occured"
		else:
			self.message = message
		
		Exception.__init__(self, status, message)
		
	
	def set_response(self):
		"""Error response handler which sets cherrypy.response status, headers, and body."""
		response = cherrypy.response
		
		#removes headers from original request
		respheaders = response.headers
		for key in ["Accept-Ranges", "Age", "ETag", "Location", "Retry-After",
					"Vary", "Content-Encoding", "Content-Length","Content-Range" , "Expires",
					"Content-Location", "Content-MD5", "Last-Modified"]:
			if respheaders.has_key(key):
				del respheaders[key]
		
		#defines response json
		response.status = self.status
		error_body = {"error": {"status": self.status,"message": self.message}}
		if cherrypy.request.show_tracebacks and not self.status == 401:
			error_body["traceback"] = format_exc()
		
		if self.status == 500 or self.status == 404:
			error_body = simplejson.dumps(error_body, indent=1)
			respheaders['Content-Length'] = len(error_body)
			respheaders['Content-Type'] = "application/json"
		
		response.body = error_body
	
	def __call__(self):
		"""Allows cherrypy to use this as a response handler"""
		raise self

class InvalidRequestError(InternalError):
	"""Exception raised when server can't parse request"""
	def __init__(self, message=None):
		if message == None:
			message = "Request was not valid"
		InternalError.__init__(self, 400, message)

class NotFoundError(InternalError):
	"""Exception raised when a URL could not be mapped to any handler (404)."""
	def __init__(self, path=None):
		if path is None:
			path = cherrypy.request.script_name + cherrypy.request.path_info
		self.args = path
		InternalError.__init__(self, 404, "The path %r was not found." % path)


def format_exc(exc=None):
	"""Return exc (or sys.exc_info if None), formatted."""
	if exc is None:
		exc = sys.exc_info()
	if exc == (None, None, None):
		return ""
	import traceback
	return "".join(traceback.format_exception(*exc))
