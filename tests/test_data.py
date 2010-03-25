"""
test_data.py

Sample data representations
"""

class Sample_JSON_Objects():
	"""Sample JSON objects"""
	track_one = {"track": {"artist": "The Arcade Fire", "title": "Ocean of Noise", "album": "Neon Bible", "duration": 213, "genre":"Rock","track_number":6,"year":None,"id":"0" }}
	track_two = {"track": {"artist": "Josh Ritter", "title": "Harrisburg", "album": "Golden Age Of Radio", "duration": 345, "genre":"Country","track_number":9,"year":None, "id":"1"}}
	track_three = {"track": {"artist": "Stevie Ray Vaughn", "title": "Little Wing", "album": "Greatest hits", "duration": 453, "genre":"Blues","track_number":None,"year":None,"id":"2"}}
	track_four = {"track": {"artist": "The Shins" ,"title": "Australia", "album": "Wincing The Night Away", "duration": 189, "genre":"indie!?","track_number":2,"year":2007,"id":"3"}}
	
	playlist = {"playlist":{"name":"test_list",
							"uri":"testing",
							"repeat":"none",
							"random":False,
							"tracks":[track_three,track_four,track_one]}}
	playlist_2 = {"playlist":  {"name":u"\u03bb unicode!",
								"uri":'%CE%BB+unicode%21',
								"repeat":"all",
								"random":True,
								"tracks":[track_two]}}
	
	playlists = {"playlists":[{"name":u'test one',"uri":u'test+one'},
										{"name":u'test two',"uri":u'test+one'},
										{"name":u'arts',"uri":u'barts'}]}
	
	status = {"status": {"current_track_id":"2",
					"state":"paused",
					"position":33,
					"volume":77}}
	error = {"error" :{"message":"An error occured",
						"status":401,
						"traceback":"sample traceback"}}

