#!/usr/bin/env python
import re
import setuptools

def parse_requirements(file_name):
	requirements = []
	for line in open(file_name, 'r').read().split('\n'):
		if re.match(r'(\s*#)|(\s*$)', line):
			continue
		if re.match(r'\s*-e\s+', line):
			# TODO support version numbers
			requirements.append(re.sub(r'\s*-e\s+.*#egg=(.*)$', r'\1', line))
		elif re.match(r'\s*-f\s+', line):
			pass
		else:
			requirements.append(line)

	return requirements

def parse_dependency_links(file_name):
	dependency_links = []
	for line in open(file_name, 'r').read().split('\n'):
		if re.match(r'\s*-[ef]\s+', line):
			dependency_links.append(re.sub(r'\s*-[ef]\s+', '', line))

	return dependency_links

setuptools.setup(name='sisyphus',
	version='0.0.1.3',
	author='mkorenkov',
	author_email = "mkorenkov@gmail.com",
	description = 'Lightweight task processing queue.',
	long_description=open('README.md').read(),
	license = "Apache License, Version 2.0",
	url = "https://github.com/mkorenkov/sisyphus",
	scripts=['bin/sisyphusd', 'bin/sisyphussched'],
	packages=setuptools.find_packages(exclude=['bin', 'samples']),
	install_requires = parse_requirements('requirements.txt'),
	dependency_links = parse_dependency_links('requirements.txt'),)