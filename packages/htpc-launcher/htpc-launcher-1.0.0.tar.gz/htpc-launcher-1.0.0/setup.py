#!/usr/bin/env python

#from distribute_setup import use_setuptools
#use_setuptools()

from setuptools import setup

from htpclauncher import PROJECT_NAME, VERSION, LAUNCH_SCRIPT

setup(
  name = PROJECT_NAME,
  version = VERSION,
  packages = ['htpclauncher'],
  py_modules = ['distribute_setup'],

  author = "Tim Court",
  author_email = "tctimmeh@gmail.com",
  description = "Launch, and switch between, full-screen applications",
  url = "https://github.com/tctimmeh/htpc-launcher",

  classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: End Users/Desktop',
    'Topic :: Multimedia',
    'License :: Public Domain',
    'Operating System :: POSIX :: Linux',
  ],

  entry_points = {
    'console_scripts': [
      '%s = htpclauncher.app:main' % LAUNCH_SCRIPT,
    ],
  }
)
