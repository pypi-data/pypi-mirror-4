import logging
import os
import signal
import threading
import time
from settings import SISYPHUS_JOIN_TTL, SISYPHUS_WORKER_TTL

class Terminator(threading.Thread):
	def __init__(self, pid, pid_file, ttl=SISYPHUS_WORKER_TTL):
		super(Terminator, self).__init__()
		self.child_pid = pid
		self.pid_file = pid_file
		self.ttl = ttl
		self.pid_file_created = False

	def run(self):
		self.timer = threading.Timer(self.ttl, self.stop)
		self.timer.start()
		while True:
			try:
				with open(self.pid_file, 'r') as pid_file:
					child_pid = pid_file.read()
					self.pid_file_created = True
			except Exception:
				child_pid = None
			if self.pid_file_created and\
			   child_pid != str(self.child_pid):
				self.wait()
				break
			time.sleep(0.1)

		if self.timer:
			self.timer.cancel()

	def wait(self):
		try:
			pid, status = os.waitpid(self.child_pid, os.WNOHANG)
		except Exception:
			pid = None
			status = None
		return pid, status

	def stop(self):
		logging.getLogger(__name__).info("%s:about to stop" % self.child_pid)
		if self.timer:
			self.timer.cancel()
		pid, status = self.wait()
		if not status:
			self.__terminate()

	def __terminate(self):
		os.kill(self.child_pid, signal.SIGTERM)
		t = threading.Timer(SISYPHUS_JOIN_TTL, self.__nuke)
		t.start()

	def __nuke(self):
		try:
			os.kill(self.child_pid, signal.SIGKILL)
		except OSError:
			pass