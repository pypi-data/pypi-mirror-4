from __future__ import unicode_literals

def throws_exception(callable, *exceptions):
	"""
	Return True if the callable throws the specified exception

	>>> throws_exception(lambda: int('3'))
	False
	>>> throws_exception(lambda: int('a'))
	True
	>>> throws_exception(lambda: int('a'), KeyError)
	False
	"""
	if not exceptions: exceptions = Exception,
	try:
		callable()
	except exceptions:
		return True
	except Exception:
		pass
	return False

def suppress_exception(callable, *exceptions):
	"""
	Call `callable` and return its result but suppress any specified
	exceptions (returning None).

	>>> suppress_exception(lambda: int('3'))
	3
	>>> suppress_exception(lambda: int('a'))
	>>> suppress_exception(lambda: int('a'), KeyError)
	Traceback (most recent call last):
	...
	ValueError: invalid literal for int() with base 10: 'a'
	"""
	if not exceptions: exceptions = Exception,
	try:
		return callable()
	except exceptions:
		pass
