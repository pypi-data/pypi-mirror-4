from itertools import starmap

def substitution(old, new):
	"""
	Return a function that will perform a substitution on a string
	"""
	return lambda s: s.replace(old, new)

def multi_substitution(*substitutions):
	"""
	Take a sequence of pairs specifying substitutions, and create
	a function that performs those substitutions.
	
	>>> multi_substitution()('')
	''
	"""
	substitutions = starmap(substitution, substitutions)
	return lambda x: x
