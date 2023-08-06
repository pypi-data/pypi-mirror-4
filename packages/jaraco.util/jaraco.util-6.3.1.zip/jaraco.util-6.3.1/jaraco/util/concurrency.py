from __future__ import absolute_import, unicode_literals

import threading
import functools

def atomize(f, lock=None):
	"""
	Decorate a function with a reentrant lock to prevent multiple
	threads from calling said thread simultaneously.
	"""
	lock = lock or threading.RLock()

	@functools.wraps(f)
	def exec_atomic(*args, **kwargs):
		lock.acquire()
		try:
			return f(*args, **kwargs)
		finally:
			lock.release()
	return exec_atomic

class AtomicGuard(object):
	"""
	A decorator that can be applied to multiple functions/methods to
	prevent more than one of them from being entered at any one time.
	"""
	def __init__(self):
		self.lock = threading.RLock()

	def __call__(self, f):
		return atomize(f, lock=self.lock)
