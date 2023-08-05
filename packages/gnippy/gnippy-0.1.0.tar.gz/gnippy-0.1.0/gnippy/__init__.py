import requests

class PowerTrackClient():
	
	def __init__(self, url, username, password, on_data_function):
		self.url = url
		self.auth = (username, password)
		self.on_data = on_data_function
		self.enabled = True
	
	
	def connect(self):
		r = requests.get(self.url, auth=self.auth, prefetch=False)
		for line in r.iter_lines():
			if not self.enabled:
				break
			elif line:
				self.on_data(line)
	
	
	def disconnect(self):
		self.enabled = False
