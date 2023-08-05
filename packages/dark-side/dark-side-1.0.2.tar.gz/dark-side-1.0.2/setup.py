#!/usr/bin/python

from distutils.core import setup


setup(name='dark-side',
      version='1.0.2',   
      description='response comparing proxy server', 
      install_requires=['gevent','requests','json_tools'],
      author='mark neyer',
      scripts=['darkside.py'])
