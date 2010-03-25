"""
server.py

Contains HowlServer, a base server class for Howl.
"""

import cherrypy

import howl, controllers

class HowlServer(object):
	"""Base server class for Howl"""
	def __init__(self):
		"""Initializes cherrypy config, loads plugins, and starts server"""
		howl.log('Loading server','HOWL')
		
		cherrypy.config.update(howl.config.server_config)
		
		howl.plugin_manager.load_all()
		
		cherrypy.tree.mount(RootController(), '/', config = howl.config.root_config)
		cherrypy.tree.mount(controllers.RestController(), '/player', config = howl.config.player_config)
	
	def start(self):
		"""Starts cherrypy server"""
		
		howl.log('Server STARTED','HOWL')
		cherrypy.engine.start()
		cherrypy.engine.block()

class RootController(object):
	"""Root controller for Howl."""
	@cherrypy.expose
	def index(self):
		"""Redirects all requests to a configured plugin."""
		raise cherrypy.HTTPRedirect('plugins/%s/' % howl.config.root_plugin_id)