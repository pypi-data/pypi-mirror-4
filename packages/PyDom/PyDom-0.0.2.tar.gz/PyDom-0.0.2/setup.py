#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='PyDom',
      version='0.0.2',
      description='Python Domotics',
      author='Jos Hendriks',
      packages=find_packages(exclude=('*test','*test.*',)),
      package_dir={'pydom': 'pydom'},
      package_data={'pydom': ['web/*', 'logging.conf', 'pyDomotics.cfg']},
      url='http://www.circuitdb.com/',
      install_requires=[
        'setuptools',
        'Inject',
        'fluidity-sm',
        'pyserial',
        'cherrypy',
        'simplejson',    
      ],
    )