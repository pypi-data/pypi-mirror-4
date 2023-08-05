#!/usr/bin/env python

"""SockJSProxy - Proxy SockJS message to/from ZeroMQ PUB/SUB sockets.

See the `samples/datereply-sjp.py` file for an example client.
"""

classifiers = """\
Development Status :: 4 - Beta
Intended Audience :: Developers
License :: OSI Approved :: MIT License
Programming Language :: Python
Topic :: Database
Topic :: Software Development :: Libraries :: Python Modules
Operating System :: Microsoft :: Windows
Operating System :: Unix"""

doclines = __doc__.split("\n")

from setuptools import setup

setup(name='sockjsproxy',
      version='0.3.1',
      description=doclines[0],
      author='Emil Ivanov',
      author_email='emil.vladev@gmail.com',
      url='https://bitbucket.org/vladev/sockjsproxy',
      packages=['sockjsproxy'],
      install_requires=['pyzmq',
                        'sockjs-tornado'
      ],
      scripts=['sockjsproxy/sockjsproxy.py',
               'sockjsproxy/samples/datereply-sjp.py'],
      license='MIT',
      classifiers = classifiers.split("\n"),
      long_description = "\n".join(doclines[2:])
)
