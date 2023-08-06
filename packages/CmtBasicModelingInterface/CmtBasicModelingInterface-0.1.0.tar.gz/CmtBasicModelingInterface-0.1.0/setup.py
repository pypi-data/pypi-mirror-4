#!/usr/bin/env python

from ez_setup import use_setuptools
use_setuptools ()
from setuptools import setup

setup (name='CmtBasicModelingInterface',
       version='0.1.0',
       description='CSDMS Basic Modeling Interface',
       author='Eric Hutton',
       author_email='eric.hutton@colorado.edu',
       url='https://csdms.colorado.edu',
       install_requires=['pylint'],
       namespace_packages=['cmt'],
       packages=['cmt.bmi', 'cmt.bmi.tests'],
       entry_points = {
           'console_scripts': [
               'bmilint = cmt.bmi.lint:main',
           ]
       },
       test_suite='cmt.bmi.tests',
      )
