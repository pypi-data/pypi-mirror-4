#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='PyDom',
      version='0.0.1',
      description='Python Domotics',
      author='Jos Hendriks',
      packages=find_packages(exclude=('*test','*test.*',)),
      url='http://www.circuitdb.com/',
      install_requires=[
        'setuptools',
        'Inject',
        'fluidity-sm',
        'pyserial',
        'cherrypy',
        'simplejson',
        'nose',
        'coverage',     
      ],
    )