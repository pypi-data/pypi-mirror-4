import functools
import pickle
from stone import PeriodicTask
from stone import Stone, PeriodicStone, Task

def stone(f):
	@functools.wraps(f)
	def decorator(*args, **kwargs):
		s = Task(f, *args, **kwargs)
		return s
	return decorator

def resurrecting_stone(every):
	def decorate(f):
		@functools.wraps(f)
		def decorator():
			s = PeriodicTask(f, every)
			return s
		return decorator
	return decorate