import unittest

import inspect, sys, pkgutil 
from time import sleep

from compass import model, ops
from compass.services import google, openstreetmap, bing

class IntegrationTestQueries(unittest.TestCase):
	def setUp(self):
		self.search = 'Belfast International Airport'
		self.services = {}
		self.queries = []
		pkg = 'compass.services'
		__import__(pkg)
		package = sys.modules[pkg]
		prefix = pkg + "."
		for importer, modname, ispkg in pkgutil.iter_modules(package.__path__, prefix):
			module = __import__(modname, locals(),[], -1)
			for name, cls in inspect.getmembers(module):
				if inspect.isclass(cls):
					try:
						obj = cls('testing compass')
						self.services[obj.__class__.__name__] = obj
						self.queries.append(ops.Query(model.Mapset(obj)))
					except Exception, e:
						print cls.__name__ + ' not tested\r\n'
		self.multi_qry = ops.Query(model.Mapset(*self.services.values()))

	def test_get_first_match(self):
		for qry in self.queries:
			sleep(1)
			result = qry.get_first_match(self.search)
			self.assertEqual(type(result), tuple)

	def test_get_all(self):
		result = self.multi_qry.get_all(self.search)
		self.assertEqual(type(result), list)

	def test_get_average(self):
		result = self.multi_qry.get_average(self.search)
		coords = []
		for qry in self.queries:
			sleep(1)
			coords.append(qry.get_first_match(self.search))
		length = len(coords)
		manual = (sum(zip(*coords)[0])/length, sum(zip(*coords)[1])/length)
		self.assertEqual(result, manual)

	def test_get_consensus(self):
		result = self.multi_qry.get_consensus(self.search)
		self.assertEqual(type(result), tuple)

if __name__ == '__main__':
    unittest.main()