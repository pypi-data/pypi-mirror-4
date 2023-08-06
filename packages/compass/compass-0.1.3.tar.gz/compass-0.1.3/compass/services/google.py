import json
from urllib import urlencode
import urllib2

from compass import model

class GMaps(model.Service):
	url = 'http://maps.googleapis.com/maps/api/geocode/json?'

	def __init__(self, ua):
		"""
		Starts limiting requests above 3 a second; 
		free maximum number of requests 2.5k/24 hours
		Can't store longer than 30 days, must be plotted on google maps

		ua User-Agent string		
		"""
		self.ua = ua

	def get(self, location):
		try:
			qs = urlencode({'address':location.encode('utf-8'),'sensor':'false'})
			req = urllib2.Request(self.url+qs)
			req.add_header('User-Agent', self.ua)
			page = urllib2.urlopen(req)
			obj = json.loads(page.read())
			lat = float(obj['results'][0]['geometry']['location']['lat'])
			lng = float(obj['results'][0]['geometry']['location']['lng'])
			return (lat,lng)
		except:
			return 0
