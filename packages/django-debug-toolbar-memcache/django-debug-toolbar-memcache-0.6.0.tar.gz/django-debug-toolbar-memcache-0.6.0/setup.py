#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='django-debug-toolbar-memcache',
    version='0.6.0',
    description='',
    author='Eirikur Nilsson',
    author_email='eirikur@gagnavarslan.is',
    url='http://github.com/Gagnavarslan/django-debug-toolbar-memcache',
    packages=find_packages(exclude=('examples', 'examples.demo', 'test')),
    provides=['debug_toolbar_memcache'],
    requires=['Django', 'debug_toolbar'],
    include_package_data=True,
    zip_safe=False,
)
