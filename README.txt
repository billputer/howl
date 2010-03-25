==========================
Howl server
==========================

Howl is a python-based web-service that provides a programmatic api for accessing the script interfaces of desktop media players.  Plugins for players like iTunes and Windows Media Player can allow users remote access to their media libraries as well as to all scriptable functions of their media players.  Additional plugins such as 'lobo' can provide a user interface to the Howl web-service.


==========================
Installation Instructions:
==========================

* To install, just type (python-2.3 or later needed):

    sudo python setup.py install

* You'll need to configure a user in the config file found at:
	~/.howl/ on Linux/Mac
	%APPDATA% on Windows
	
* To run server, type:
	
	howl