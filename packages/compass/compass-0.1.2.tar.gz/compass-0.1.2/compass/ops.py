
STRATEGY_TYPES = ['first', 'all', 'consensus', 'average']

class Query():

	def __init__(self, mapset):
		self.mapset = mapset

	def get_first_match(self, query):
		"""
		Returns first valid location 
		Queries APIs in order of position added to Mapset
		"""
		for service in self.mapset.services:
			result = service.get(query)
			if result:
				return result
		return 0

	def get_all(self, query, as_dict=False):
		"""
		Returns a list or dict of all valid locations
		"""
		if as_dict:
			results = {}
			for service in self.mapset.services:
				results[service.__class__.__name__] = service.get(query)
		else:
			results = []
			for service in self.mapset.services:
				results.append(service.get(query))
		return results

	def get_average(self, query):
		"""
		Naive average: returns median of all successful queries
		including outliers
		"""
		coords = []
		for service in self.mapset.services:
			coords.append(service.get(query))
		length = len(coords)
		if length:
			return (sum(zip(*coords)[0])/length, sum(zip(*coords)[1])/length)
		else:
			return 0

	def get_consensus(self, query):
		"""
		Average position excluding outliers
		"""
		return 0