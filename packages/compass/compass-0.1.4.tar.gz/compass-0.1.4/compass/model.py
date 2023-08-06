import abc

class Service( object ):
	__metaclass__ = abc.ABCMeta

	@abc.abstractmethod
	def get(self, location):
		"""
		Do the lookup, return the lat/lon tuple

		location: String representing address to search
		"""

class Mapset():
	
	def __init__(self, *args):
		self.services = args

	def add(self, service):
		self.services.append(service)
