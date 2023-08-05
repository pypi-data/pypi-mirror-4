import logging
from sisyphus.master import Master
from sisyphus.scheduler_logic import SchedulerLogic
from sisyphus.utils import import_module, inspect_auto_stones
from sisyphus.logger import Logger

def worker(imports):
	logging.setLoggerClass(Logger)
	logging.root = Logger(__name__)

	for m in imports.split(","):
		import_module(m)
	m = Master()
	m.run()

def scheduler(imports):
	logging.setLoggerClass(Logger)
	logging.root = Logger(__name__)

	auto_stones = []
	for m in imports.split(","):
		tasks = import_module(m)
		auto_stones_parts = inspect_auto_stones(tasks)
		auto_stones.extend(auto_stones_parts)
	m = SchedulerLogic(auto_stones)
	m.run()