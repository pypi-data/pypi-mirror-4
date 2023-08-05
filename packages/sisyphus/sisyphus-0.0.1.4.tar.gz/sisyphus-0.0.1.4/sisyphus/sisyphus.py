import logging
import os
import threading
import signal
import time
from settings import SISYPHUS_JOIN_TTL

class Sisyphus(threading.Thread):
	def __init__(self, stone, pid_file, logger=None, ttl=SISYPHUS_JOIN_TTL):
		super(Sisyphus, self).__init__()
		self.stone = stone
		self.join_ttl = ttl
		self.logger = logger
		self.pid_file = pid_file
		signal.signal(signal.SIGTERM, self.terminate)

	@property
	def pid(self):
		return os.getpid()

	def run(self):
		with open(self.pid_file, 'w') as f:
			f.write(str(self.pid))
		time.sleep(0.1)
		self.stone.run()
		time.sleep(0.1)
		os.remove(self.pid_file)
		os._exit(0)

	def terminate(self, signum=None, frame=None):
		if self.pid:
			os.remove(self.pid_file)

			if self.logger:
				self.logger.error("%s terminating" % self.pid)
			else:
				logging.error("%s terminating" % self.pid)

			threading.Timer(self.join_ttl, self.nuke)
			os._exit(1)

	def nuke(self):
		if self.pid:
			if self.logger:
				self.logger.error("%s terminated" % self.pid)
			else:
				logging.error("%s terminated" % self.pid)

			try:
				os.kill(self.pid, sig=signal.SIGKILL)
				os._exit(1)
			except OSError:
				pass

