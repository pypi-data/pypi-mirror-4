#!/usr/bin/env python

from distutils.core import setup
from web import __version__

setup(name = 'pyobj',
      version = '1.0',
      description = 'generic python object creation',
      author = 'Leonardo Rossetti',
      author_email = 'motw.leo@gmail.com',
      url = 'https://bitbucket.org/goldark/pyobj',
      packages = ['pyobj'],
      long_description = 'Create and pass python objects as class methods/functions parameter.',
      license = "Public domain",
      platforms = ["any"],
)