#!/usr/bin/env python
'''
Created on Apr 2, 2013

@author: jonathanfriedman

Version parsing is adopted from:
http://stackoverflow.com/questions/458550/standard-way-to-embed-version-into-python-package
'''
from distutils.core import setup

## get version info
import re
VERSIONFILE="pysurvey/_version.py"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^version = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))

setup(name='PySurvey',
      version=verstr,
      author='Jonathan Friedman',
      author_email='yonatanf@mit.edu',
      license='MIT',
      packages=['pysurvey',
                'pysurvey.analysis',
                'pysurvey.analysis.component_dist',
                'pysurvey.core',
                'pysurvey.io',
                'pysurvey.plotting',
                'pysurvey.plotting.interactive',
                'pysurvey.sandbox',
                'pysurvey.sandbox.untb',
                'pysurvey.tests',
                'pysurvey.util',
                'pysurvey.util.InformationTheory',
                ],
      package_data={'pysurvey.tests': ['data/*'],},
      long_description=open('README.rst').read(),
      install_requires=[
        "pandas >= 0.8.0",
        ],
      test_suite='nose.collector',
      test_requires=['Nose'],
      )