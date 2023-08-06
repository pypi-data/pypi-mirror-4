import json
from urllib import urlencode
import urllib2

from compass import model

class OSMap(model.Service):
	url = 'http://nominatim.openstreetmap.org/search?'

	def __init__(self, ua):
		"""
		1 req/sec minimum between reqs for osm

		ua User-Agent string
		"""
		self.ua = ua

	def get(self, location):
		try:
			qs =urlencode({'q':location.encode('utf-8'),'format':'json'})
			req = urllib2.Request(self.url+qs)
			req.add_header('User-Agent', self.ua)
			page = urllib2.urlopen(req)
			obj = json.loads(page.read())
			lat = float(obj[0]['lat'])
			lng = float(obj[0]['lon'])
			return (lat,lng)
		except:
			return 0
