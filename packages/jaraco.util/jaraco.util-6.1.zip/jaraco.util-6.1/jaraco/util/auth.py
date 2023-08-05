from __future__ import absolute_import, unicode_literals

import codecs
import random
import itertools

class PasswordGenerator(object):
	"""
	Generates random passwords
	>>> pw = PasswordGenerator.make_password(8, encoding=None)
	>>> len(pw)
	8

	>>> pw != PasswordGenerator.make_password(8, encoding=None)
	True

	>>> pw = PasswordGenerator.make_password(8, encoding='hex')
	>>> type(pw) == str
	True
	>>> set(pw) <= set('0123456789abcdef')
	True
	"""

	@staticmethod
	def make_password(n_bytes = 8, encoding = 'base-64'):
		'Make a password with n_bytes of disorder; optionally encoded'
		chars = PasswordGenerator.get_random_chars(n_bytes)
		result = ''.join(chars).encode('latin-1')
		null_encoder = lambda s: (s, len(s))
		encoder = codecs.getencoder(encoding) if encoding else null_encoder
		encoded, length = encoder(result)
		return encoded

	@staticmethod
	def get_random_chars(len):
		return itertools.islice(PasswordGenerator.random_byte_generator(), len)

	@staticmethod
	def random_byte_generator():
		while True:
			yield unichr(random.randint(0, 255))
