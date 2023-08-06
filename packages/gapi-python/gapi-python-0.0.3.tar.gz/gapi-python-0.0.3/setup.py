#!/usr/bin/env python
from setuptools import setup, find_packages

packages=['gapipy']

setup(
    name='gapi-python',
    packages=packages,
    version='0.0.3',
    author='G Adventures',
    author_email='software@gadventures.com',
    description='Python client for the G Adventures REST API',
    install_requires = ['requests>=1.0.4'], 
)
