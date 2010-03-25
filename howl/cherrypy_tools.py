"""
cherrypy_tools.py

cherrypy_tools contains tools for CherryPy for processing incoming and outoing JSON data
cherrypy_tools also contains a custom dispatcher to allow HTTP method overloading
"""

__author__ = 'William Wiens'

import cherrypy
import re, urllib
import simplejson
import howl.error as error

json_encoder = simplejson.JSONEncoder()

mime_types = ["application/json"]

def process_request():
	"""CherryPy Tool for processing JSON from incoming requests"""
	headers = cherrypy.request.headers
	#checks for a body, then parses and validates if there is one
	if cherrypy.request.body and headers.has_key('Content-Type') and not headers['Content-Length'] == '0':
		if headers['Content-Type'] == "application/json":
			body = cherrypy.request.body.read()
			try:
				cherrypy.request.validated_data = simplejson.loads(body)
			except:
				raise error.InvalidRequestError("Invalid json in:\t%s" % body)
		else:
			raise error.InvalidRequestError("Invalid content type: %s" + cherrypy.request.headers['Content-Type'])

cherrypy.tools.process_request = cherrypy.Tool('before_handler', process_request)

def process_response():
	"""CherryPy Tool for encoding JSON in responses"""
	if cherrypy.response.body and not cherrypy.response.headers['Content-Type'] == 'audio/mpeg':
		mime_type = cherrypy.tools.accept.callable(mime_types)
		cherrypy.response.headers['Content-Type'] = mime_type
		if not type(cherrypy.response.body) == str:
			cherrypy.response.body = json_encoder.iterencode(cherrypy.response.body)


cherrypy.tools.process_response = cherrypy.Tool('before_finalize', process_response)

class OverloadDispatcher(cherrypy.dispatch.MethodDispatcher):
	"""
	Custom dispatcher written to allow overloading of POST for clients who don't support full range of HTTP headers.
	"""
	
	def __call__(self, path_info):
		"""Utilizes X-Http-Method-Override to allow clients to specify HTTP method in headers."""
		headers = cherrypy.request.headers
		
		if headers.has_key("X-Http-Method-Override"):
			cherrypy.request.method = headers["X-Http-Method-Override"]
		super(OverloadDispatcher, self).__call__(path_info)