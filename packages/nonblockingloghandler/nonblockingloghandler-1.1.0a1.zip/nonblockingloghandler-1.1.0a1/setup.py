from setuptools import setup
setup(name='nonblockingloghandler',
      version='1.1.0a1',
      author='Somethinkodd Development Team',
      author_email='logging@somethinkodd.com',
      url='http://somethinkodd.com/nonblockingloghandler',
      py_modules=['nonblockingloghandler', 'autoclosingqueue' ],
      test_suite = "nonblockingloghandler.test.test_all_nonblockingloghandler",
      description='Nonblocking Logging Handler for Python Logging',
      classifiers=["Development Status :: 5 - Production/Stable",
                   "Intended Audience :: Developers",
                   "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python",
                   "Topic :: System :: Logging",
                  ],
      long_description="""
Provides a NonblockingLogHandler class consistent with the Python logging subsystem.

This handler acts as a proxy for the another log handler that may be slow to execute: e.g. the SMTPHandler, SocketHandler,
SysLogHandler - especially when they are talking to remote servers.

If you have a real-time system (i.e. one where a late response is a wrong response) and you are sending log messages via email,
http, syslog, etc., you should consider using this module to protect against unexpected delays.

It is intended to be a drop-in replacement (with some minor provisos) for the proxied handler which returns quickly, and executes
the actually logging in the background, in a separate thread.""",
     )
