
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
		Average position using only the closest grouped results.
		As there is such a small population outliers or more typically, 
		the outlier, is calculated using a somewhat non-standard measure:
		Any lat/lon outside one standard deviation from the mean is discounted. 
		"""
		vals = self.get_all(query)
		length = len(vals)
		avg = (sum(zip(*vals)[0])/length, sum(zip(*vals)[1])/length)
		std_dev = []
		for idx, coord_vector in enumerate([vector for vector in zip(*vals)]):
			inter_std_dev = []
			for val in coord_vector:
				inter_std_dev.append((val - avg[idx])**2)
			std_dev.append((sum(inter_std_dev)/len(inter_std_dev))**(0.5))
		for idx, coord_vector in enumerate([vector for vector in zip(*vals)]):
			for idy, val in enumerate(coord_vector):
				if abs(avg[idx] - val) > abs(std_dev[idx]):
					vals[idy] = 0
		vals = [keep_val for keep_val in vals if keep_val]
		length = len(vals)
		return ( sum(zip(*vals)[0])/length, sum(zip(*vals)[1])/length)
