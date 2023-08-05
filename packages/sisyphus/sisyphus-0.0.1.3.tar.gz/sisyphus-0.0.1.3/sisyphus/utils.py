import os
import sys
from datetime import datetime
import inspect
import imp
import pytz
from settings import AUTO_DECORATOR_NAME

def now(tz=None):
	if tz:
		return datetime.now(tz=pytz.timezone(tz))
	else:
		return datetime.now()

def module_by_name(module_name):
	current_module = sys.modules[module_name]
	return current_module

def function_by_name(module, name):
	all_functions = inspect.getmembers(module, inspect.isfunction)
	valid = filter(lambda x: x[0] == name, all_functions)
	if len(valid):
		return valid[0][1]
	return None

def inspect_auto_stones(module):
	auto_stone_names = methods_with_decorator(module=module, decorator_name=AUTO_DECORATOR_NAME)
	all_functions = inspect.getmembers(module, inspect.isfunction)

	auto_stone_names = list(auto_stone_names)
	auto_stones = filter(lambda x: x[0] in auto_stone_names, all_functions)
	return auto_stones

def methods_with_decorator(module, decorator_name):
	source_lines = inspect.getsourcelines(module)[0]
	for i,line in enumerate(source_lines):
		line = line.strip()
		if line.split('(')[0].strip() == '@'+decorator_name: # leaving a bit out
			nextLine = None
			function_line_number = i
			while True:
				function_line_number += 1
				nextLine = source_lines[function_line_number]
				if not len(nextLine):
					continue
				elif nextLine.strip()[0]=="@":
					continue
				else:
					break
			name = nextLine.split('def')[1].split('(')[0].strip()
			yield name

def import_module(path):
	mod_name,file_ext = os.path.splitext(os.path.split(path)[-1])

	parts = path.split("/")[:-1]
	if len(parts):
		sys.path.append("/".join(parts))

	if file_ext.lower() == '.py':
		py_mod = imp.load_source(mod_name, path)
	elif file_ext.lower() == '.pyc':
		py_mod = imp.load_compiled(mod_name, path)
	else:
		raise NotImplementedError()
		#todo: add support for module by folder

	return py_mod
