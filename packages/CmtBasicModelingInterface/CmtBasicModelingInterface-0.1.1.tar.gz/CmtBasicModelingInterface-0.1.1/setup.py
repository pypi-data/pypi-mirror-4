#!/usr/bin/env python

from ez_setup import use_setuptools
use_setuptools ()
from setuptools import setup, find_packages

setup (name='CmtBasicModelingInterface',
       version='0.1.1',
       description='CSDMS Basic Modeling Interface',
       long_description=open('README.rst').read(),
       author='Eric Hutton',
       author_email='eric.hutton@colorado.edu',
       url='https://csdms.colorado.edu',
       install_requires=['pylint', 'CmtStandardNames'],
       namespace_packages=['cmt'],
       packages=['cmt', 'cmt.bmi', 'cmt.bmi.tests', 'cmt.bmi.examples',
                 'cmt.bmi.examples.water_tank'],
       #packages=find_packages(),
       entry_points = {
           'console_scripts': [
               'bmilint = cmt.bmi.lint:main',
               'water_tank = cmt.bmi.examples.water_tank:main',
               'rainfall = cmt.bmi.examples.rainfall:main',
               'rain_in_tank = cmt.bmi.examples.rain_in_tank:main',
           ]
       },
       test_suite='cmt.bmi.tests',
      )
