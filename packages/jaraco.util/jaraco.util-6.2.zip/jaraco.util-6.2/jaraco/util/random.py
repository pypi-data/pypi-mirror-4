from __future__ import absolute_import, unicode_literals

import random
import struct

def bytes(n):
	"""
	Returns n random bytes

	>>> res = list(bytes(5))
	>>> assert len(res) == 5
	>>> assert all(len(b) == 1 for b in res)
	"""
	for i in range(n // 4):
		for byte in struct.pack('f', random.random()):
			yield byte
	for byte in struct.pack('f', random.random())[: n % 4]:
		yield byte
