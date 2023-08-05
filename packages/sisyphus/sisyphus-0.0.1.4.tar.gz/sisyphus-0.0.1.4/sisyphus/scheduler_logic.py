from datetime import datetime
import logging
import pickle
import time
from pika.exceptions import AMQPChannelError
from connection import connection
from settings import SISYPHUS_SCHEDULER_QUEUE_NAME, SISYPHUS_WORKER_QUEUE_NAME
from publisher import publish
from utils import function_by_name, module_by_name, now
from subscriber import subscribe

SLEEP=0.1

class SchedulerLogic:
	def __init__(self, auto_stones, worker_queue=SISYPHUS_WORKER_QUEUE_NAME, internal_queue=SISYPHUS_SCHEDULER_QUEUE_NAME, purge_queue_on_start=True):
		self.__stop = False
		self.worker_queue = worker_queue
		self.internal_queue = internal_queue
		with connection() as channel:
			if purge_queue_on_start:
				try:
					channel.queue_delete(queue=self.internal_queue)
				except AMQPChannelError:
					pass

			self.logger = logging.getLogger(__name__)
			self.logger.info("loading tasks")
			for method in auto_stones:
				stone = method[1]()
				self.logger.info("Loaded task: %s schedule %s" % (stone.__name__, stone.every))
				stone.delay()

	def consume(self, message):
		message_loaded = pickle.loads(message)
		stone = message_loaded
		if stone.eta <= now():
			publish(message, queue=self.worker_queue)
			self.logger.info("scheduled %s task execution" % stone.name)
			stone.move_next()
			#print "next execution: %s" % stone.eta
			publish(pickle.dumps(stone), queue=self.internal_queue)
		else:
			#print "%s eta %s" % (stone.name, stone.eta)
			publish(message, queue=self.internal_queue)
		time.sleep(SLEEP)

	def run(self):
		subscribe(self.consume, queue=self.internal_queue, late_ack=True)
