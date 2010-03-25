"""
controllers.py

Controllers defines cherrypy controllers for the 'player' REST service.
"""

import cherrypy

import howl
import error

class RestController(object):
	"""
	RestController defines the root of the /player/ uri structure
	CherryPy maps URI structure to object structure, so a call to
	/player/status/ will map to the Status Controller of this object
	
	"""
	exposed = True
	
	def __init__(self):
		self.status = Status_Controller()
		self.playlists = Playlist_Controller()
		self.tracks = Track_Controller()
	
	def GET(self):
		raise cherrypy.HTTPRedirect('player/status/')


class Playlist_Controller(object):
	"""Handles all requests to playlist/ URIs"""
	exposed = True
	
	def __init__(self):
		self.player = howl.plugin_manager.player_plugin
	
	def GET(self, playlist_id = None, playlist_attr = None, attr_index = None):
		"""
		All GET requests to /player/playlists/ are mapped here.
		If the URI has additional values, like /player/playlists/454/tracks/
		then those are passed in as arguments
		"""
		#request to 'playlists'
		if not playlist_id:
			return {'playlists': [pl.GET(with_tracks = False) for pl in self.player.playlists.itervalues()]}
		
		try:
			pl = self.player.playlists[playlist_id].GET()
		except KeyError:
			raise error.InvalidRequestError("Unable to find playlist with id '%s'" % playlist_id)
		
		#request to 'playlists/playlist_id'
		if not playlist_attr:
			return pl
		
		try:
			attr = pl['playlist'][playlist_attr]
		except KeyError:
			raise error.InvalidRequestError("Playlist has no attribute '%s'" % playlist_attr)
		
		#request to 'playlists/playlist_id/playlist_attribute'
		if not attr_index:
			return {playlist_attr: attr}
		
		#request to 'playlists/playlist_id/playlist_attribute/attribute_index'
		try:
			return attr[int(attr_index)]
		except KeyError:
			raise error.InvalidRequestError("Playlist attribute '%s' has no value at index '%s'" % (playlist_attr, attr_index))
			
	
	
	def POST(self):
		"""
		All POST requests to /player/playlists/ are mapped here.
		This method creates a new playlist with a name defined
		in the request body
		"""
		new_name = cherrypy.request.validated_data['playlist']['name']
		new_playlist = self.player.Playlist.POST(new_name)
		self.player.playlists[new_playlist.id] = new_playlist
		cherrypy.response.status = 201
		cherrypy.response.headers["Location"] = new_playlist.uri
	
	def PUT(self, playlist_id):
		"""
		All PUT requests to /player/playlists/ are mapped here.
		This method modifies a playlist with the json in the request body
		"""
		try:
			pl = self.player.playlists[playlist_id]
		except KeyError:
			raise error.InvalidRequestError("Unable to find playlist with id '%s'" % playlist_id)
		
		pl.PUT(cherrypy.request.validated_data)
	
	def DELETE(self, playlist_id):
		"""
		All DELETE requests to /player/playlists/ are mapped here.
		This method deletes a playlist from the media player
		"""
		try:
			pl = self.player.playlists[playlist_id]
		except KeyError:
			raise error.InvalidRequestError("Unable to find playlist with id '%s'" % playlist_id)
		
		self.player.playlists.pop(pl.id)
		pl.DELETE()
	
	_cp_config = {	"tools.process_request.on": True,
					"tools.process_response.on": True}

class Status_Controller(object):
	"""Handles all requests to status/ URIs"""
	exposed = True
	
	def __init__(self):
		self.status = howl.plugin_manager.player_plugin.Status()
	
	def GET(self, tag = None):
		"""
		All GET requests to /player/status/ are mapped here.
		If the URI has an additional value, like /status/current_track/
		then it is passed in as an argument
		"""
		if tag:
			try:
				return {'status': {tag: getattr(self.status, tag)}}
			except AttributeError:
				raise error.InvalidRequestError("%s is not a valid status attribute." % attr_name)
		else:
			return self.status.get_json()
	
	def PUT(self, attr = None):
		"""
		All PUT requests to /player/status/ are mapped here.
		If the URI has an additional value, like /status/current_track/
		then it is passed in as an argument
		"""
		new_status = cherrypy.request.validated_data['status']
		for name in ['current_track_id','volume','state','position']:
			if new_status.has_key(name) and new_status[name]:
				setattr(self.status, name, new_status[name])
	
	_cp_config = {	'tools.process_request.on': True,
					'tools.process_response.on': True}

class Track_Controller(object):
	"""
	Handles all requests to tracks/ URIs
	Allows read-only access to all of a media player's tracks
	"""
	exposed = True
	
	def __init__(self):
		self.player = howl.plugin_manager.player_plugin
	
	def GET(self, track_id = None, tag = None):
		"""
		All GET requests to /player/tracks/ are mapped here.
		If the URI has additional values, like /player/tracks/349438/file
		then those are passed in as arguments
		"""
		if not track_id:
			tracks = []
			for pl in self.player.playlists.itervalues():
				tracks.extend(pl.GET()['playlist']['tracks'])
			return {'tracks': tracks}
		
		track = self.player.Track(track_id = track_id)
		
		if not tag:
			return track.get_json()
		
		if tag == 'file':
			return cherrypy.lib.static.serve_file(track.get_path(), content_type='audio/mpeg')
		else:
			raise error.InvalidRequestError("The track attribute '%s' is not addressable." % tag)
	
	_cp_config = {	'tools.process_request.on': True,
					'tools.process_response.on': True,
					'request.stream': True}
