#!/usr/bin/env python
# encoding=UTF-8
import os
from setuptools import setup

try:
    import multiprocessing
except ImportError:
    pass


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(name='pymonon',
      version=__import__('pymonon').__version__,
      description='Python Money Helper',
      long_description=read('README.rst'),
      author=u'Pedro Buron',
      author_email='pedroburonv@gmail.com',
      url='https://github.com/pedroburon/pymonon',
      test_suite='nose.collector',
      packages=['pymonon'],
      tests_require=['nose'],
      setup_requires=['distribute'],
      classifiers=[
          'Development Status :: 1 - Planning',
          'Programming Language :: Python :: 2 :: Only',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Office/Business :: Financial :: Accounting',
      ]
      )
