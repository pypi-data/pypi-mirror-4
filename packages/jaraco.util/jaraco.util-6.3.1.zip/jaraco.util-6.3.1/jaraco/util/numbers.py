from __future__ import unicode_literals

def ordinalth(n):
	"""Return the ordinal with 'st', 'th', or 'nd' appended as appropriate.
	>>> list(map(str, map(ordinalth, range(-5, 22))))
	['-5th', '-4th', '-3rd', '-2nd', '-1st', '0th', '1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th', '10th', '11th', '12th', '13th', '14th', '15th', '16th', '17th', '18th', '19th', '20th', '21st']
	"""
	# zero through three map to 'th', 'st', 'nd', 'rd'
	t = ('th', 'st', 'nd', 'rd')
	# special case: ones digit is > 3
	ones = abs(n) % 10
	forceth = ones > 3
	# special case: n ends in 11, 12, 13
	forceth |= abs(n) % 100 in (11, 12, 13)
	index = [ones, 0][forceth]
	return '%d%s' % (n, t[index])

def coerce(value):
	"""
	coerce takes a value and attempts to convert it to a float,
	or int.

	If none of the conversions are successful, the original value is
	returned.

	>>> coerce('3')
	3L

	>>> coerce('foo')
	u'foo'
	"""
	result = value
	for transform in (float, long):
		try: result = transform(value)
		except ValueError: pass

	return result
