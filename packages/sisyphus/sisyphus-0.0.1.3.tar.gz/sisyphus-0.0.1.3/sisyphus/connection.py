import pika
from contextlib import contextmanager

@contextmanager
def connection(host="127.0.0.1"):
	c = pika.BlockingConnection(pika.ConnectionParameters(host))
	channel = c.channel()
	try:
		yield channel
	finally:
		if c is not None:
			c.close()