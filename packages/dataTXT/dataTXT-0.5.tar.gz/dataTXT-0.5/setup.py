#!/usr/bin/env python

from distutils.core import setup

__version__ = '0.5'

setup(name='dataTXT',
      version=__version__,
      description="python interface for SpazioDati's dataTXT and DBpedia",
      long_description=open('README.txt', 'r').read(),
      author="Marco Amadori",
      author_email="amadori@spaziodati.eu",
      url="https://github.com/SpazioDati/python-datatxt",
      py_modules=['datatxt'],
      scripts=["example/datatxt-cli"],
      install_requires=['sparql-client >= 0.13', 'requests >= 0.11'],
      license='LICENSE.TXT',
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

