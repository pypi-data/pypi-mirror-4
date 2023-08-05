#!/usr/bin/env python
import setuptools

setuptools.setup(name='sisyphus',
	version='0.0.1.4',
	author='mkorenkov',
	author_email = "mkorenkov@gmail.com",
	description = 'Lightweight task processing queue.',
	long_description='Lightweight task processing queue.', #open('README.md').read(),
	license = "Apache License, Version 2.0",
	url = "https://github.com/mkorenkov/sisyphus",
	scripts=['bin/sisyphusd', 'bin/sisyphussched'],
	packages=setuptools.find_packages(exclude=['bin', 'samples']),
	install_requires = ["distribute","pika","wsgiref","pytz","croniter"], #parse_requirements('requirements.txt'),
	#dependency_links = parse_dependency_links('requirements.txt'),
)
