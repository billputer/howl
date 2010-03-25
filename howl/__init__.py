"""
__init__.py

Howl is a python-based webserver that provides a programmatic api for accessing the
script interfaces of desktop media players.	 Plugins for players like iTunes and Windows
Media Player can allow users remote access to their media libraries as well as to
all scriptable functions of their media players.  Additional plugins such as 'howl'
provide a user interface to the Howl web-service.

This file, __init__.py provides functions for running the Howl server as a script
"""

__author__ = 'William Wiens'
__version__ = '0.6'

import optparse
import platform

import server
import config_tools
import plugin_tools

platform = platform.system()
config = config_tools.Config()
plugin_manager = plugin_tools.PluginManager()

def main():
	"""Function called when Howl is run as a command-line script"""
	desc = """A command line script which starts the Howl server."""
	parser = optparse.OptionParser(description = desc, version = __version__)
	options, args = parser.parse_args()
	
	server.HowlServer().start()



if __name__ == "__main__":
	main()