"""
Utility functions to facilitate object comparison without __cmp__

Based on recipe found at http://code.activestate.com/recipes/510403/
"""

from __future__ import unicode_literals

class RichComparisonMixin(object):
	"""
	Define __cmp__, and inherit from this class to provide full rich
	comparisons.
	"""

	def __eq__(self, other):
		return self.__cmp__(other) == 0

	def __ne__(self, other):
		return self.__cmp__(other) != 0

	def __lt__(self, other):
		return self.__cmp__(other) < 0

	def __le__(self, other):
		return self.__cmp__(other) <= 0

	def __gt__(self, other):
		return self.__cmp__(other) > 0

	def __ge__(self, other):
		return self.__cmp__(other) >= 0

class KeyedEqualityMixin(object):

	def __eq__(self, other):
		return self.__key__() == other.__key__()

	def __ne__(self, other):
		return self.__key__() != other.__key__()

class KeyedComparisonMixin(KeyedEqualityMixin):
	def __lt__(self, other):
		return self.__key__() < other.__key__()

	def __le__(self, other):
		return self.__key__() <= other.__key__()

	def __gt__(self, other):
		return self.__key__() > other.__key__()

	def __ge__(self, other):
		return self.__key__() >= other.__key__()

class KeyedHashingMixin(KeyedEqualityMixin):
	def __hash__(self):
		return hash(self.__key__())
