#!/usr/bin/env python

from ez_setup import use_setuptools
use_setuptools ()
from setuptools import setup, find_packages

setup (name='CmtBasicModelingInterface',
       version='0.1.2',
       description='CSDMS Basic Modeling Interface',
       long_description=open('README.rst').read(),
       author='Eric Hutton',
       author_email='eric.hutton@colorado.edu',
       url='https://csdms.colorado.edu',
       install_requires=['pylint', 'CmtStandardNames'],
       namespace_packages=['cmt'],
       packages=find_packages(),
       entry_points = {
           'console_scripts': [
               'bmilint = cmt.bmi.lint:main',
               'water_tank = cmt.bmi.examples.water_tank.water_tank:main',
               'rainfall = cmt.bmi.examples.water_tank.rainfall:main',
               'rain_in_tank = cmt.bmi.examples.water_tank.rain_in_tank:main',
           ]
       },
       test_suite='cmt.bmi.tests',
      )
