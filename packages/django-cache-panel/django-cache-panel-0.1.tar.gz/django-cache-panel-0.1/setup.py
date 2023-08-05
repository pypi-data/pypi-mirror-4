#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='django-cache-panel',
    version='0.1',
    description='A more detailed cache panel for the Django Debug Toolbar',
    author='Brandon Konkle',
    author_email='brandon@lincolnloop.com',
    url='http://github.com/lincolnloop/django-cache-panel',
    packages=find_packages(),
    provides=['cache_panel'],
    requires=['Django', 'debug_toolbar'],
    include_package_data=True,
    zip_safe=False,
)
