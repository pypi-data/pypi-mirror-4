from datetime import datetime
import pickle
import marshal
from publisher import publish
from settings import SISYPHUS_SCHEDULER_QUEUE_NAME
from utils import module_by_name, function_by_name

class Task:
	def __init__(self, callable, *args, **kwargs):
		self.__wrapped = callable
		self.args = args
		self.kwargs = kwargs
		if hasattr(callable, '__name__'):
			self.__name__ = self.name = callable.__name__
		if hasattr(callable, '__module__'):
			self.__module__ = self.name = callable.__module__
		if hasattr(callable, '__doc__'):
			self.__doc__ = callable.__doc__

	def __getattr__(self, k):
		return getattr(self.wrapped, k)

	def run(self, *args, **kwargs):
		return self.__wrapped(*args, **kwargs)

	def __call__(self, *args, **kwargs):
		return self.__wrapped(*args, **kwargs)

	def delay(self):
		args = []
		args.extend(self.args)
		kwargs = self.kwargs.copy()

		module = module_by_name(self.__module__)
		method = function_by_name(module, self.__name__)
		publish(message=pickle.dumps(Stone(method, *args, **kwargs)))

class PeriodicTask(Task):
	def __init__(self, callable, every):
		Task.__init__(self, callable)
		self.every = every

	def delay(self):
		module = module_by_name(self.__module__)
		method = function_by_name(module, self.__name__)
		publish(message=pickle.dumps(PeriodicStone(method, self.every)), queue=SISYPHUS_SCHEDULER_QUEUE_NAME)

class Stone:
	def __init__(self, method, *args, **kwargs):
		self._callable = method
		self.args = args
		self.kwargs = kwargs

	@property
	def callable(self):
		return self._callable

	@property
	def name(self):
		return self._callable.__name__

	def run(self):
		return self.callable().run(*self.args, **self.kwargs)

class PeriodicStone(Stone):
	def __init__(self, method, every):
		Stone.__init__(self, method)
		if not every:
			raise NameError("Param 'every=' should be set")
		self.every=every
		self.__eta=self.every.next

	@property
	def eta(self):
		if not self.__eta:
			self.__eta = self.every.next
		return datetime.fromtimestamp(self.__eta)

	def move_next(self):
		self.every.move_next()
		self.__eta = self.every.next

	def fix_callable(self):
		module = module_by_name(self.__module__)
		method = function_by_name(module, self.__name__)
		self._callable = method
