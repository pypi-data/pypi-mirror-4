import json
from urllib import urlencode
import urllib2

from compass import model

class BMaps(model.Service):
	url = 'http://dev.virtualearth.net/REST/v1/Locations?'

	def __init__(self, ua, key):
		"""
		free maximum 50k/24 hours with a bing map/internal app

		ua User-Agent string
		key Your bing maps api key https://www.bingmapsportal.com/
		"""
		self.ua = ua
		self.key = key

	def get(self, location):
		try:
			qs = urlencode({'query':location.encode('utf-8'), 
				'o':'json', 'key':self.key})
			req = urllib2.Request(self.url+qs)
			req.add_header('User-Agent', self.ua)
			page = urllib2.urlopen(req)
			obj = json.loads(page.read())
			lat = float(
				obj['resourceSets'][0]['resources'][0]['point']['coordinates'][0])
			lng = float(
				obj['resourceSets'][0]['resources'][0]['point']['coordinates'][1])
			return (lat,lng)
		except:
			return 0