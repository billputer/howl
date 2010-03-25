"""
http_test.py

tests howl http responses
requires a running copy of howl on localhost to run
"""

import unittest
import random

from test_utils import WebCase

test_playlist_name = "howl_test"
test_username = "test_user"
test_password = "test"

class TestStatusRequests(WebCase):
	"""Tests manipulation of status object"""
	
	def testSetStatus(self):
		"""Sets and retrieves status"""
		self.getPage("player/status/")
		self.assertResponse(status = 200,body_type="status")
		self.assertHeader('content-type','application/json')
		
		new_status = {"status":{"state":"playing"}}
		self.getPage("player/status/",method="PUT", body=new_status)
		self.assertStatus(200)
		
		self.getPage("player/status/")
		self.assertResponse(status = 200,body_type="status")
		self.assert_(self.body["status"]["state"] == "playing")
		
		self.getPage("player/playlists/C9A801D36E94BA36")
		track_id = self.body["playlist"]["tracks"][0]["track"]["id"]
		new_status = {"status": {"current_track_id":track_id}}
		self.getPage("player/status/",method="PUT",body=new_status)
		self.assertStatus(200)
		
		fail_status = {"status":{"state":"failure!"}}
		self.getPage("player/status/",method="PUT",body = fail_status)
		self.assertResponse(status = 400,body_type="error")
		
		new_status = {"status":{"state":"paused"}}
		self.getPage("player/status/",method="PUT", body=new_status)
		self.assertStatus(200)

class TestPlaylists(WebCase):
	"""Tests playlist manipulation"""
	
	def testCreateUpdateAndDelete(self):
		"""Tests Create, Update, and Delete operations on playlists"""
		
		body = {'playlist': {'name': test_playlist_name}}
		self.getPage("player/playlists/", method = "POST", body=body)
		self.assertStatus(201)
		new_playlist_uri = self.headers["location"]
		
		#retrieves new playlist body
		self.getPage(new_playlist_uri, method = "GET")
		self.assertResponse(status = 200,body_type="playlist")
		new_playlist = self.body
		
		new_tracks = self.getRandomSongs(3)
		
		#add the five songs to new playlist and PUT to server
		new_playlist["playlist"]["tracks"] = new_tracks
		self.getPage(new_playlist_uri, method = "PUT",body = new_playlist)
		self.assertStatus(200)
		
		#retrieve servers copy of playlist
		self.getPage(new_playlist_uri, method = "GET")
		self.assertResponse(status = 200, body_type="playlist")
		self.assert_(new_playlist == self.body)
		
		self.getPage(new_playlist_uri, method = "DELETE")
		self.assertStatus(200)
	
	def getRandomSongs(self, num_songs):
		"""picks 'num_songs' random songs from a random playlist"""
		
		#retrieves a random playlist
		self.getPage("player/playlists/", method = "GET")
		self.assertResponse(status = 200,body_type="playlists")
		random_list_uri = random.choice(self.body["playlists"])['playlist']['uri']
		
		#chooses 'num_songs' different tracks
		new_tracks = []
		self.getPage(random_list_uri)
		self.assertResponse(status = 200,body_type="playlist")
		random_list_tracks = self.body["playlist"]["tracks"]
		
		if not random_list_tracks:
			self.getRandomSongs(num_songs)
		for x in range(0,num_songs):
			random_track = random.choice(random_list_tracks)
			new_tracks.append(random_track)
		return new_tracks
	
	def testGetPlaylists(self):
		"""Tests playlist retreival"""
		
		self.getPage("player/playlists/", method = "GET")
		self.assertResponse(status = 200,body_type="playlists")
		playlists = self.body["playlists"]
		
		#picks five random playlists to query
		for x in range(0,5):
			random_list = random.choice(playlists)
			random_list_uri = random_list['playlist']['uri']
			self.getPage(random_list_uri, method = "GET")
			self.assertResponse(status = 200,body_type="playlist")

class TestAuth(WebCase):
	"""Tests authentication"""
	
	def testBasicAuth(self):
		"""Tests basic authentication"""
		
		self.client.clear_credentials()
		for page in ["player/playlists/","player/status/"]:
			self.getPage(page,method="GET")
			self.assertStatus(401)
			
		
		self.client.clear_credentials()
		self.client.add_credentials("test_none","asdf")
		for page in ["player/playlists/","player/status/"]:
			self.getPage(page,method="GET")
			self.assertStatus(401)
		
		self.client.clear_credentials()
		self.client.add_credentials(test_username, test_password)
		
		for page in ["player/playlists/"]:
			self.getPage(page,method="GET")
			self.assertStatus(200)
		
		self.getPage("player/status/",method="GET")
		self.assertStatus(200)
		new_state = {"status":{"state":"paused"}}
		self.getPage("player/status/state",method="PUT",body = new_state)
		self.assertStatus(200)


if __name__ == '__main__':
	#suite = unittest.TestLoader().loadTestsFromTestCase(TestAuth)
	#unittest.TextTestRunner(verbosity=2).run(suite)
	
	unittest.main()
		
		
		