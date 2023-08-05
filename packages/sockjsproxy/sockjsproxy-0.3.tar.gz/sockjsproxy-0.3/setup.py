#!/usr/bin/env python

from setuptools import setup

setup(name='sockjsproxy',
      version='0.3',
      description='A proxy server that proxies SockJS message to/from a ZeroMQ socket',
      author='Emil Ivanov',
      author_email='emil.vladev@gmail.com',
      url='https://bitbucket.org/vladev/sockjsproxy',
      packages=['sockjsproxy'],
      install_requires=['pyzmq',
                        'sockjs-tornado'
      ],
      scripts=['sockjsproxy/sockjsproxy.py',
               'sockjsproxy/samples/datereply-sjp.py'],
      license='MIT'
)
