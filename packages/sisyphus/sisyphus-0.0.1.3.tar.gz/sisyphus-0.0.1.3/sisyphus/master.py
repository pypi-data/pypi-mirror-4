import logging
import os
import pickle
import tempfile
import time
from settings import SISYPHUS_WORKER_TTL, SISYPHUS_JOIN_TTL
from sisyphus import Sisyphus
from subscriber import subscribe
from terminator import Terminator

class Master:
	def __init__(self, logger = None, ttl=SISYPHUS_WORKER_TTL):
		self.logger = logger
		self.ttl = ttl

	def run(self):
		subscribe(self.on_stone_received)

	def on_stone_received(self, stone):
		pid_file = tempfile.mktemp()
		stone = pickle.loads(stone)
		logging.getLogger(__name__).info("received %s task from broker" % stone.name)
		child_pid = os.fork()
		time.sleep(0.1)
		if not child_pid:
			#child
			s = Sisyphus(stone, pid_file, ttl=SISYPHUS_JOIN_TTL)
			s.run()
			time.sleep(0.1)
		else:
			#master
			t = Terminator(child_pid, pid_file, ttl=SISYPHUS_WORKER_TTL)
			t.start()
			time.sleep(0.1)