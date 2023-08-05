#!/usr/bin/env python
import setuptools

setuptools.setup(name='django-sisyphus',
	version='0.0.1.1',
	author='Max Korenkov',
	author_email = "mkorenkov@gmail.com",
	description = 'Sisyphus task processing queue django app.',
	license = "Apache License, Version 2.0",
	url = "https://github.com/mkorenkov/django-sisyphus",
	packages=setuptools.find_packages(),
	install_requires = ["sisyphus"])
