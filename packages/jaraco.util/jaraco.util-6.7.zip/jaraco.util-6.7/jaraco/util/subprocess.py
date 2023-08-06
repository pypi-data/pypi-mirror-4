from __future__ import absolute_import
import sys
import subprocess
import threading
import Queue as queue

def enqueue_lines(stream, queue):
	for line in iter(stream.readline, b''):
		queue.put(line)
	stream.close()

# copy attribute for convenience
PIPE=subprocess.PIPE

def Popen_nonblocking(*args, **kwargs):
	"""
	Open a subprocess without blocking. Return a process handle with any
	output streams replaced by queues of lines from that stream.

	Usage:

	proc = Popen_nonblocking(..., stdout=subprocess.PIPE)
	try:
		out_line = proc.stdout.get_nowait()
	except queue.Empty:
		"no output available"
	else:
		handle_output(out_line)
	"""
	kwargs.setdefault('close_fds', 'posix' in sys.builtin_module_names)
	kwargs.setdefault('bufsize', 1)
	proc = subprocess.Popen(*args, **kwargs)
	if proc.stdout:
		q = queue.Queue()
		t = threading.Thread(target=enqueue_lines,
			args=(proc.stdout, q))
		proc.stdout = q
		# thread dies with the parent
		t.daemon = True
		t.start()
	if proc.stderr:
		q = queue.Queue()
		t = threading.Thread(target=enqueue_lines,
			args=(proc.stderr, q))
		proc.stderr = q
		t.daemon = True
		t.start()
	return proc
