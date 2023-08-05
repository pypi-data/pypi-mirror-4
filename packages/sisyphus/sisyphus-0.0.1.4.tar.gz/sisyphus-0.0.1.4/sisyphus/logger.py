import logging
import sys
import settings

class ConsoleHandler(logging.StreamHandler):
	def __init__(self):
		logging.StreamHandler.__init__(self)
		self.stream = None # reset it; we are not going to use it anyway

	def emit(self, record):
		if record.levelno >= logging.ERROR:
			self.__emit(record, sys.stderr)
		self.__emit(record, sys.stdout)

	def __emit(self, record, strm):
		self.stream = strm
		logging.StreamHandler.emit(self, record)

	def flush(self):
		# Workaround a bug in logging module
		# See:
		#   http://bugs.python.org/issue6333
		if self.stream and hasattr(self.stream, 'flush') and not self.stream.closed:
			logging.StreamHandler.flush(self)

class Logger(logging.Logger):
	def __init__(self, name=__name__):
		super(Logger, self).__init__(name)
		console = ConsoleHandler()
		formatter = logging.Formatter('%(levelname)s - %(asctime)s - %(module)s - %(message)s')
		console.setFormatter(formatter)

		self.addHandler(console)
		self.setLevel(settings.LOG_LEVEL)
		self.propagate = False
