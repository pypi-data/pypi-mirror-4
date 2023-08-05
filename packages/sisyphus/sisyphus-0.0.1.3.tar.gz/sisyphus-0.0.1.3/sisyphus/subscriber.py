import pickle
import time
import marshal
from connection import connection
from settings import SISYPHUS_WORKER_QUEUE_NAME

class Subscriber():
	def __init__(self, callback, queue, late_ack=False):
		self.queue = queue
		self.channel = None
		self.__callback = callback
		self.__late_ack = late_ack

	def callback(self, ch, method, properties, body):
		if not self.__late_ack:
			ch.basic_ack(delivery_tag = method.delivery_tag)
		self.__callback(body)
		if self.__late_ack:
			ch.basic_ack(delivery_tag = method.delivery_tag)
		time.sleep(0.1)

	def start(self):
		self.run()

	def run(self):
		with connection() as channel:
			self.channel = channel
			channel.queue_declare(queue=self.queue, durable=True)
			channel.basic_consume(self.callback,
				queue=self.queue)
			channel.basic_qos(prefetch_count=1)
			channel.start_consuming()

	def stop(self):
		if self.channel:
			self.channel.stop_consuming()

def subscribe(callback, queue=SISYPHUS_WORKER_QUEUE_NAME, late_ack=False):
	s = Subscriber(callback, queue, late_ack)
	s.start()