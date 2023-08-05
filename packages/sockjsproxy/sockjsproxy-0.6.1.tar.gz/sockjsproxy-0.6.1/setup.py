#!/usr/bin/env python

"""SockJSProxy - Proxy SockJS message to/from ZeroMQ PUB/SUB sockets.

See the `samples/datereply-sjp.py` file for an example client.

Development Status :: 4 - Beta
Intended Audience :: Developers
License :: OSI Approved :: MIT License
Programming Language :: Python
Topic :: Database
Topic :: Software Development :: Libraries :: Python Modules
Operating System :: Microsoft :: Windows
Operating System :: Unix
"""

desc, long_desc, classifiers = __doc__.split("\n\n")

from setuptools import setup, find_packages

setup(name='sockjsproxy',
      version='0.6.1',
      author='Emil Ivanov',
      author_email='emil.vladev@gmail.com',
      url='https://bitbucket.org/vladev/sockjsproxy',
      packages=find_packages(),
      install_requires=['pyzmq',
                        'sockjs-tornado'],
      scripts=['bin/sockjsproxy',
               'sockjsproxy/samples/datereply-sjp.py'],
      package_data={
          '': ['samples/*.html', 'samples/js/*.js']
      },
      license='MIT',
      description=desc,
      classifiers=[c for c in classifiers.split("\n") if c],
      long_description=long_desc,
      zip_safe=False
)
