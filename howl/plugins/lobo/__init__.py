"""
__init__.py

Lobo client plugin
"""

import cherrypy
import pkg_resources

import howl.plugin_tools

def get_plugin():
	return LoboPlugin

class LoboPlugin(howl.plugin_tools.CherryPyPlugin):
	"""Plugin for serving the Lobo flash application"""
	identifier = 'lobo'
	description = 'This plugin serves a flash application which allows for both local and remote playback.'
	platform = 'All'
	
	def __init__(self):
		lobo_directory = pkg_resources.resource_filename(__name__, 'bin')
		self.config = {'/':
						{"tools.staticdir.on": True,
					 	"tools.staticdir.dir": lobo_directory}}
		
		howl.log("'%s' loaded" % self.identifier, 'PLUGINS')
	
	@cherrypy.expose
	def index(self):
		"""Serves Lobo html and swf"""
		raise cherrypy.InternalRedirect("lobo.html")