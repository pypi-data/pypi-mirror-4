
from contextlib import contextmanager

@contextmanager
def context(name):
	print 'entering context', name
	yield name
	print 'leaving context', name

class Context(object):
	def __init__(self, name):
		self.name = name

	def __enter__(self):
		print 'entering context', self.name

	def __exit__(self, *args, **kwargs):
		print 'leaving context', self.name

with Context('first') as first:
	with Context('second') as second:
		raise Exception
