import threading
import time
from connection import connection
from settings import SISYPHUS_WORKER_QUEUE_NAME
from settings import SISYPHUS_WORKER_TTL

class Publisher(threading.Thread):
	def __init__(self, message, queue, count=1):
		super(Publisher, self).__init__()
		self.message = message
		self.queue = queue
		self.max_count = count
		self.count = 0

	def run(self):
		with connection() as channel:
			channel.queue_declare(queue=self.queue, durable=True)
			while self.count < self.max_count:
				channel.basic_publish(exchange="",
					routing_key=self.queue,
					body=self.message)

				self.count += 1
				time.sleep(0.5)

	def stop(self):
		self.max_count = -1
		self.join(SISYPHUS_WORKER_TTL)

def publish(message, queue=SISYPHUS_WORKER_QUEUE_NAME):
	p = Publisher(message, queue)
	p.start()