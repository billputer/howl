"""
itunes_plugin_test.py

tests itunes_mac plugin functionality
"""

import unittest, random, time

import simplejson

from appscript import CommandError, app, its, k

import howl.error as error
import howl

class Test_Status(unittest.TestCase):
	"""Test status object"""
	
	def setUp(self):
		"""Initializes status object"""
		self.status = howl.plugins.itunes_mac.Status()
	
	def test_state(self):
		"""Tests manipulation of possible player states"""
		self.status.state = "playing"
		self.assertEqual(self.status.state, "playing")
		
		self.status.state = "paused"
		self.assertEqual(self.status.state, "paused")
		
		self.status.state = "stopped"
		self.assertEqual(self.status.state, "stopped")
		
		self.assertRaises(error.InvalidRequestError, setattr, self.status, 'state', 'fail')
	
	def test_position(self):
		"""Tests manipulation of current position"""
		track = self.status.current_track
		if not track:
			self.status.state = 'playing'
			track = self.status.current_track
		track_duration = track['track']['duration']
		self.status.position = int(track_duration - 10)
		self.assertEqual(self.status.position, int(track_duration - 10))
		
		self.assertRaises(error.InvalidRequestError, setattr, self.status, 'position', track_duration + 10.0)
	
	def test_volume(self):
		"""Tests volume manipulation"""
		original_volume = self.status.volume
		
		new_volume = 66
		self.status.volume = new_volume
		self.assertEqual(self.status.volume, new_volume)
		
		invalid_volume = -12
		self.assertRaises(error.InvalidRequestError, setattr, self.status, 'volume', invalid_volume)
		invalid_volume = 200
		self.assertRaises(error.InvalidRequestError, setattr, self.status, 'volume', invalid_volume)
		
		self.status.volume = original_volume

class Test_Playlist(unittest.TestCase):
	"""Tests Playlist object"""
	
	def setUp(self):
		playlist_ref = random.choice([pl for pl in app('iTunes').user_playlists.get() if pl.special_kind.get() == k.none])
		self.test_playlist = howl.plugins.itunes_mac.Playlist(playlist_ref)
		self.test_track = random.choice(self.test_playlist.tracks)

	def test_playlist_init(self):
		self.assert_(self.test_playlist.name)
		self.assert_(self.test_playlist.uri)
		self.assertEqual(type(self.test_playlist.special),bool)

	def test_GET(self):
		self.assert_(simplejson.dumps(self.test_playlist.GET()))
		self.assert_(simplejson.dumps(self.test_track.get_json()))

	def test_random(self):
		"""Tests manipulation of playlists random attribute"""
		init_random = self.test_playlist.get_random()

		self.test_playlist.set_random(True)
		self.assertEqual(self.test_playlist.get_random(),True)

		self.test_playlist.set_random(False)
		self.assertEqual(self.test_playlist.get_random(),False)

		self.assertRaises(error.InvalidRequestError, self.test_playlist.set_random, 5)

		self.test_playlist.set_random(init_random)

	def test_repeat(self):
		"""Tests manipulation of playlists repeat attribute"""
		repeat = self.test_playlist.get_repeat()
		for new_repeat in ["one","all","off"]:
			self.test_playlist.set_repeat(new_repeat)
			self.assertEqual(self.test_playlist.get_repeat(), new_repeat)

		self.assertRaises(error.InvalidRequestError, self.test_playlist.set_repeat, "fail")

		self.test_playlist.set_repeat(repeat)
	
if __name__ == '__main__':
	unittest.main()
