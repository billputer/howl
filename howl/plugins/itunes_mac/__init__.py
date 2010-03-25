"""
__init__.py

iTunes plug-in for howl (mac os-x specific)
Utilizes appscript package to make scripting calls to iTunes OSA interface.
"""

from appscript import CommandError, app, its, k

import howl.error as error
import howl.plugin_tools

def get_plugin():
	return iTunesExtension

class iTunesExtension(howl.plugin_tools.PlayerExtension):
	"""
	Interface to the iTunes media player.
	Takes all commmands and sends them via appscript to iTunes.
	All references to playlists and tracks are done by ID unless otherwise noted
	"""
	identifier = 'itunes_mac'
	description = 'This plugin provides Howl access to the Applescript interface of iTunes for OS X.'
	platform = 'Darwin'
	
	def __init__(self):
		"""Sets identifiers and initializes current playlist"""
		self.Status = Status
		self.Playlist = Playlist
		self.Track = Track
		
		self.playlists = self.load_playlists()
		
		howl.log("'%s' loaded" % self.identifier, 'PLUGINS')
	
	def load_playlists(self):
		"""Loads all playlists from iTunes"""
		howl.log("Loading playlists for '%s'" % self.identifier, 'PLUGINS')
		playlists = {}
		for pl in app('iTunes').user_playlists.get():
			if pl.special_kind.get() == k.none:
				new_playlist = self.Playlist(playlist_ref = pl)
				playlists[new_playlist.id] = new_playlist
		return playlists


class Status(object):
	"""
	Exposes iTunes state (volume, current track, position) as properties.
	"""
	
	def get_json(self):
		"""Returns a JSON representation of player status"""
		status = {}
		for tag in ['current_track_id','current_track','volume','state','position']:
			status[tag] = getattr(self, tag)
		return {'status': status}
	
	#Following code uses Pythons 'property' function so that
	#we can avoid using getters and setters externally
	#and just access iTunes data as properties
	
	def _get_current_track_id(self):
		"""Track ID of currently playing track."""
		try:
			return Track(track_ref = app('iTunes').current_track).id
		except CommandError:
			return ""
	
	def _set_current_track_id(self, new_track_id):
		try:
			track_ref = app('iTunes').user_playlists['Music'].file_tracks[its.persistent_ID==new_track_id].first()
		except CommandError:
			raise error.InvalidRequestError("Current track id '%s' not found" % new_track_id)
		
		state = self.state
		app('iTunes').play(track_ref)
		if state == 'stopped':
			self.state = 'paused'
		else:
			self.state = state
	
	current_track_id = property(_get_current_track_id, _set_current_track_id)
	
	def _get_current_track(self):
		"""Current track information in JSON.	 Read-only."""
		try:
			return Track(track_ref = app('iTunes').current_track()).get_json()
		except CommandError:
			return {}
	current_track = property(_get_current_track)
	
	
	
	def _get_state(self):
		"""Current state of iTunes (playing, paused, etc)"""
		return app('iTunes').player_state().name
	
	def _set_state(self, new_state):
		if new_state == "playing":
			if not self.state == 'playing':
				try:
					app('iTunes').current_track() #throws an exception if there is no current track
					app('iTunes').play(app('iTunes').current_track)
				except CommandError:
					pass
		elif new_state == "stopped":
			app('iTunes').stop()
		elif new_state == "paused":
			app('iTunes').pause()
		else:
			raise error.InvalidRequestError("%s is not a valid state." % new_state)
	
	state = property(_get_state, _set_state)
	
	def _get_position(self):
		"""Position of currently playing track"""
		pos = app('iTunes').player_position()
		if pos == k.missing_value: #if we are stopped
			pos = 0
		return pos
	
	def _set_position(self, value):
		try:
			duration = app('iTunes').current_track.duration()
			if value > duration or value < 0:
				raise error.InvalidRequestError("Track position %s is not valid" % value)
			app('iTunes').player_position.set(value)
		except CommandError:
			raise error.InvalidRequestError("Cannot set position when iTunes has no current track.")
	
	position = property(_get_position, _set_position)
	
	def _get_volume(self):
		"""Current iTunes volume"""
		return app('iTunes').sound_volume()
	
	def _set_volume(self,new_v):
		if new_v > 100 or new_v < 0:
			raise error.InvalidRequestError("'%s' is not a valid volume." % new_v)
		app('iTunes').sound_volume.set(new_v)
	
	volume = property(_get_volume, _set_volume)


class Playlist(object):
	"""Class representing an interface to iTunes playlist"""
	
	def __init__(self, playlist_ref = None, playlist_id = None):
		if playlist_ref:
			self.ref = playlist_ref
		elif playlist_id:
			self.ref = app('iTunes').user_playlists['Music'][its.persistent_ID==playlist_id].first()[0]
		else:
			error.InvalidRequestError("Playlist must be initialized with either a reference or id")
		self.name = self.ref.name()
		self.id = self.ref.persistent_ID()
		self.uri = 'player/playlists/%s' % self.id
		self.special = (self.ref.special_kind.get() != k.none)
		self.tracks = [Track(track_ref = x) for x in self.ref.file_tracks.get()]
	
	def GET(self, with_tracks = True):
		"""Returns an JSON representation of the playlist"""
		json = {'name': self.name,
				'id': self.id,
				'uri': self.uri,
				'repeat': self.get_repeat(),
				'random': self.get_random()}
		if with_tracks:
			json['tracks'] = [t.get_json() for t in self.tracks]
		return {'playlist': json}
	
	def PUT(self, new_playlist):
		"""Modifies the tracks in an iTunes playlist"""
		if self.special:
			raise error.InvalidRequestError("Attempted to change special playlist '%s'" % self.ref.name)
		
		new_tracks = new_playlist['playlist']['tracks']
		new_ids = [track["track"]["id"] for track in new_tracks]
		
		try:
			current_ids = self.ref.tracks.persistent_ID.get()
		except CommandError:
			current_ids = []
		
		#remove all tracks no longer in list
		for i, current_id in enumerate(current_ids):
			if not new_ids.count(current_id):
				self.ref.tracks[its.persistent_ID == current_id].delete()
				del current_ids[i]
		
		#add all new tracks to list
		for new_id in new_ids:
			if not current_ids.count(new_id):
				new_track = app('iTunes').user_playlists['Music'].file_tracks[its.persistent_ID == new_id].first()
				app('iTunes').duplicate(new_track, to=self.ref)
		
		#rearrange new list
		for index, track_id in enumerate(new_ids):
			location_reference = self.ref.tracks[index+1].before
			track = self.ref.tracks[its.persistent_ID == track_id].first()
			app('iTunes').move(track,to=location_reference)
		
		self.tracks = [Track(track_ref = x) for x in self.ref.file_tracks.get()]
	
	@classmethod
	def POST(self, name):
		"""Class method which creates an iTunes playlist and returns a Playlist object"""
		new_list_ref = app('iTunes').make(new = k.user_playlist, with_properties={k.name: name})
		return Playlist(playlist_ref = new_list_ref)
	
	def DELETE(self):
		"""Deletes a playlist from iTunes"""
		if self.special:
			raise error.InvalidRequestError("Attempted to delete special playlist '%s'" % pl.name)
		else:
			app('iTunes').delete(self.ref)
	
	def get_random(self):
		"""Returns a playlists random value (also known as shuffle)"""
		return self.ref.shuffle()
	
	def set_random(self, new_random):
		"""Sets a playlists random value"""
		if not type(new_random) == bool:
			raise error.InvalidRequestError("Attempted to assign an invalid random value")
		self.ref.shuffle.set(new_random)
	
	def get_repeat(self):
		"""Returns a playlists repeat value.  Can be either repeat all, none, or one"""
		return self.ref.song_repeat().name
	
	def set_repeat(self, new_repeat):
		"""Sets a playlists repeat value"""
		if new_repeat not in ["one","all","off"]:
			raise error.InvalidRequestError("Attempted to assign an invalid repeat value")
		k_enum = getattr(k,new_repeat)
		self.ref.song_repeat.set(k_enum)



class Track(object):
	"""Class representing an interface to iTunes track"""
	
	"""Tags Howl uses for tracks"""
	valid_tags = ["artist","title", "album", "duration", "genre","track_number","year","id"]
	""""Provides a mapping for howl tags that are different than the iTunes tag name"""
	tag_translation = {"title":"name","id":"persistent_ID"}
	
	def __init__(self, track_ref = None, track_id = None):
		if track_ref:
			self.ref = track_ref
		elif track_id:
			try:
				self.ref = app('iTunes').user_playlists['Music'].file_tracks[its.persistent_ID == track_id].first()
			except CommandError:
				raise error.InvalidRequestError("Current track id '%s' not found" % track_id)
		else:
			error.InvalidRequestError("Track must be initialized with either a reference or id")
		
		self.id = self.ref.persistent_ID()
		self.uri = 'player/tracks/%s' % self.id
	
	def get_json(self):
		"""Returns Track object in JSON"""
		json = {}
		
		for tag in self.valid_tags:
			if self.tag_translation.has_key(tag):
				it_tag = self.tag_translation[tag]
			else:
				it_tag = tag
			json[tag] = getattr(self.ref, it_tag)()
		json['uri'] = self.uri
		return {"track": json}
	
	def get_path(self):
		"""Returns filesystem location of this track"""
		return self.ref.location().path

