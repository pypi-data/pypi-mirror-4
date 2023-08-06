#!/usr/bin/env python
import os
import sys

from funkymetrics import __version__
from setuptools import setup

def publish():
    """Publish to Pypi"""
    os.system("python setup.py sdist upload")

if sys.argv[-1] == "publish":
    publish()
    sys.exit()

setup(name='django-funkymetrics',
      version=__version__,
      description='Super simple Django application for easily tracking events and submitting them asynchronously to KISSmetrics.',
      long_description=open('README.md').read(),
      author='Funkbit AS',
      author_email='post@funkbit.no',
      url='https://github.com/funkbit/django-funkymetrics',
      packages=['funkymetrics', ],
      license='BSD',
      classifiers=(
        "Development Status :: 4 - Beta",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        )
     )
