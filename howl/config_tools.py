"""
config_tools.py

config_tools defines a Config class for reading and holding configuration values.
"""

import md5
import os
import shutil
import ConfigParser
import pkg_resources

import cherrypy

import howl
import howl.cherrypy_tools

class Config(object):
	"""Reads user config file and maintains server config"""
	
	server_config = {'server.thread_pool': 10,
					'server.socket_host': '0.0.0.0',
					'checker.on': True,
					'request.show_tracebacks': False,
					'tools.trailing_slash.on': False,
					'tools.gzip.on': True,
					'tools.decode.on': True,
					'tools.encode.on': True,
					'tools.basic_auth.on': True,
					'tools.basic_auth.realm': 'localhost',
					'engine.autoreload_on': False,					
					}
	root_config = {'/favicon.ico':
					{'tools.staticfile.on': True,
					'tools.staticfile.filename': pkg_resources.resource_filename(__name__,'assets/FavIcon.ico')}}
	
	player_config = {'/': {'request.dispatch': howl.cherrypy_tools.OverloadDispatcher()}}
	
	def __init__(self):
		"""Reads user config and initializes log and error handlers"""
		#uses the cherrypy logger to log events
		howl.log = cherrypy.log
		
		#overrides cherrypy error handlers with our own
		cherrypy.NotFound = howl.error.NotFoundError
		cherrypy.HTTPError = howl.error.InternalError
		
		config_parser = self.get_config_parser()
		#create a dict containing usernames and digests of passwords
		users = {}
		for user in config_parser.items('users'):
			users[user[0]] = md5.new(str(user[1])).hexdigest()
		
		self.users = users
		self.port = config_parser.getint("howl", "port")
		self.root_plugin_id = config_parser.get('howl', 'root_plugin')
		self.player_plugin_id = config_parser.get('howl', 'player_plugin')
		
		self.server_config.update({'tools.basic_auth.users': self.users})
		self.server_config.update({'server.socket_port': self.port})
	
	def get_config_parser(self):
		"""Returns a SafeConfigParser object from the howl.conf config file"""
		if howl.platform == 'Darwin':
			config_folder_path = os.path.expanduser('~/.howl/')
		elif howl.platform == 'Linux':
			config_folder_path = os.path.expanduser('~/.howl/')
		elif howl.platform == 'Windows':
			config_folder_path = os.environ['APPDATA'] + 'Howl'
		else:
			raise Exception('Invalid platform')
		
		if not os.path.exists(config_folder_path):
			os.mkdir(config_folder_path)
		
		config_file_path = config_folder_path + 'howl.conf'
		
		if not os.path.exists(config_file_path):
			default_config_file = pkg_resources.resource_filename(__name__, 'assets/howl.conf')
			shutil.copy(default_config_file, config_folder_path)
		
		config_parser = ConfigParser.SafeConfigParser()
		config_parser.read(config_file_path)
		return config_parser