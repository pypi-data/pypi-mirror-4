#!/usr/bin/env python

try:
    from setuptools import setup
except:
    from distutils.core import setup

from datatxt import __version__ as version

setup(name='dataTXT',
      version=version,
      description="python interface for SpazioDati's dataTXT and DBpedia",
      long_description=open('README.rst', 'r').read(),
      author="Marco Amadori",
      author_email="amadori@spaziodati.eu",
      url="https://github.com/SpazioDati/python-datatxt",
      py_modules=['datatxt'],
      install_requires=['sparql-client>=0.13', 'requests>=0.11'],
      license='BSD',
      classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Natural Language :: Italian',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Topic :: Database',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Indexing'
      ],
      )

