#!/usr/bin/env python
'''
Created on Apr 2, 2013

@author: jonathanfriedman
'''
from distutils.core import setup

setup(name='PySurvey',
      version='0.1.0',
      author='Jonathan Friedman',
      author_email='jyonatanf@mit.edu',
      license='MIT',
      packages=['pysurvey',
                'pysurvey.analysis',
                'pysurvey.core',
                'pysurvey.io',
                'pysurvey.plotting',
                'pysurvey.plotting.interactive',
                'pysurvey.util',
                'pysurvey.util.InformationTheory',
                'pysurvey.tests',
                'pysurvey.sandbox',
                'pysurvey.sandbox.untb',
                ],
      long_description=open('README.rst').read(),
      install_requires=[
        "pandas >= 0.8.0",
        ],
      )