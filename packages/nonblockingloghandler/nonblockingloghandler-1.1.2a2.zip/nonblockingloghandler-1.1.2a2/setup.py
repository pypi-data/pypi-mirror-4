from setuptools import setup
from nonblockingloghandlerversion import __version__
setup(name='nonblockingloghandler',
      version=__version__,
      author='Somethinkodd Development Team',
      author_email='logging@somethinkodd.com',
      url='http://somethinkodd.com/nonblockingloghandler',
      py_modules=['nonblockingloghandler', 'autoclosingqueue', 'nonblockingloghandlerversion'],
      test_suite = "nonblockingloghandler.test.test_all_nonblockingloghandler",
      description='Nonblocking Logging Handler for Python Logging',
      classifiers=["Development Status :: 5 - Production/Stable",
                   #"Development Status :: 3 - Alpha",
                   "Intended Audience :: Developers",
                   "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python",
                   "Topic :: System :: Logging",
                  ],
      long_description=file("README.txt", "r").read()
     )
