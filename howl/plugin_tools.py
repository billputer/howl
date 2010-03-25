"""
plugin_tools.py

Contains Plugin Manager and base classes for Howl plugins
"""
import howl
import pkg_resources
import cherrypy

class PluginBase(object):
	"""Base plugin class, all plugins need a unique identifier and a description"""
	identifier = ''
	description = ''
	platform = 'All' #platform can be either 'all', 'Linux', 'Windows', or 'Darwin'
	plugin_type = None


class PlayerExtension(PluginBase):
	"""Base class for all media player extensions"""
	plugin_type = 'player_plugin'

class CherryPyPlugin(PluginBase):
	"""Base class for all extensions to howl's CherryPy service"""
	plugin_type = 'cherrypy_plugin'

class PluginManager(dict):
	"""Class which loads all plugins from 'plugins/' folder"""
	loaded = {}
	player_plugin = None
	
	def __init__(self):
		"""Imports all plugin modules based on platform"""
		for modname in pkg_resources.resource_listdir(__name__,'plugins'):
			if pkg_resources.resource_exists(__name__, 'plugins/%s/__init__.py' % modname):
				plugin = __import__('plugins.%s' % modname, globals(), locals(), ['']).get_plugin()
				if plugin.platform == 'All' or plugin.platform == howl.platform:
					self[modname] = plugin
	
	def load_plugin(self, plugin_name):
		"""Initializes a plugin and loads into URI tree depending on type"""
		if self.has_key(plugin_name):
			plugin = self[plugin_name]()
			self.loaded[plugin.identifier] = plugin
			if plugin.plugin_type == 'cherrypy_plugin':
				cherrypy.tree.mount(plugin, '/plugins/%s' % plugin.identifier, config = plugin.config)
	
	def load_all(self):
		"""Initializes all plugins and sets player plugin"""
		for plugin_name in self.iterkeys():
			self.load_plugin(plugin_name)
		if hasattr(howl.config, 'player_plugin_id'):
			try:
				self.player_plugin = self.loaded[howl.config.player_plugin_id]
			except KeyError:
				raise Exception("Howl cannot find player plugin with id: '%s'" % howl.config.player_plugin_id)
	