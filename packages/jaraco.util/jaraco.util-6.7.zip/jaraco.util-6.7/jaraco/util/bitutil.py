from __future__ import absolute_import, unicode_literals

from functools import reduce

# consider Brandon Craig Rhoades presentation at PyCon 2010 for a new
#  implementation to get bit values.
# http://us.python.org/2010/conference/schedule/event/12/
"""
def bits(n):
	n += 2**32
	return bin(n)[-32:]
"""

def get_bit_values(number, size=32):
	"""
	Get bit values as a list for a given number

	>>> get_bit_values(1) == [0]*31 + [1]
	True

	>>> get_bit_values(0xDEADBEEF)
	[1, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1]

	You may override the default word size of 32-bits to match your actual
	application.
	>>> get_bit_values(0x3, 2)
	[1, 1]

	>>> get_bit_values(0x3, 4)
	[0, 0, 1, 1]
	"""
	values = list(gen_bit_values(number))
	# 0-pad the most significant bit
	res = [0] * (size - len(values))
	res.extend(reversed(values))
	return res

def gen_bit_values(number):
	"""
	Return a zero or one for each bit of a numeric value up to the most
	significant 1 bit, beginning with the least significant bit.
	"""
	number = long(number)
	while number:
		yield int(number & 0x1)
		number >>= 1

def coalesce(bits):
	"""
	Take a sequence of bits, most significant first, and
	coalesce them into a number.

	>>> coalesce([1,0,1])
	5
	"""
	operation = lambda a, b: (a << 1 | b)
	return reduce(operation, bits)

class Flags(object):
	"""
	Subclasses should define _names, a list of flag names beginning
	with the least-significant bit.

	>>> MyFlags = type(str('MyFlags'), (Flags,), dict(_names=tuple('abc')))
	>>> mf = MyFlags.from_number(5)
	>>> mf['a']
	1
	>>> mf['b']
	0
	>>> mf['c'] == mf[2]
	True
	>>> mf['b'] = 1
	>>> mf['a'] = 0
	>>> mf.number
	6
	"""
	def __init__(self, values):
		self._values = list(values)
		if hasattr(self, '_names'):
			n_missing_bits = len(self._names) - len(self._values)
			self._values.extend([0] * n_missing_bits)

	@classmethod
	def from_number(cls, number):
		return cls(gen_bit_values(number))

	@property
	def number(self):
		return coalesce(reversed(self._values))

	def __setitem__(self, key, value):
		# first try by index, then by name
		try:
			self._values[key] = value
		except TypeError:
			index = self._names.index(key)
			self._values[index] = value

	def __getitem__(self, key):
		# first try by index, then by name
		try:
			return self._values[key]
		except TypeError:
			index = self._names.index(key)
			return self._values[index]

class BitMask(type):
	"""
	A metaclass to create a bitmask with attributes. Subclass an int and
	set this as the metaclass to use.

	>>> class MyBits(int):
	...   __metaclass__ = BitMask
	...   a = 0x1
	...   b = 0x4
	...   c = 0x3

	>>> b1 = MyBits(3)
	>>> b1.a, b1.b, b1.c
	(True, False, True)
	>>> b2 = MyBits(8)
	>>> any([b2.a, b2.b, b2.c])
	False
	"""

	def __new__(cls, name, bases, attrs):
		newattrs = dict(
			(attr, property(lambda self, value=value: bool(self & value)))
			for attr, value in attrs.items()
			if not attr.startswith('_')
		)
		return type.__new__(cls, name, bases, newattrs)
