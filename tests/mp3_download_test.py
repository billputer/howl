"""
mp3_download_test.py

tests file download functionality
"""

import unittest

from test_utils import WebCase, print_timing

#Change this to a track in your library
TRACK_ID = 'BA8CF36B0505329E'

class TestDownload(WebCase):
	"""Simple test to download an MP3"""
	
	#@print_timing
	def testSimple(self):
		"""Downloads a single mp3"""
		
		self.getPage("player/tracks/%s/file" % TRACK_ID,convert_body=False)
		self.assertStatus(200)
		print self.headers
		#save_file = file("test_track.mp3","w")
		#save_file.write(self.body)
		#save_file.close()
		
		
if __name__ == '__main__':
	unittest.main()
	


