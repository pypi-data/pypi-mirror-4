#!/usr/bin/env python

from distutils.core import setup
import pyCloudy

setup(name='pyCloudy',
      version=pyCloudy.__version__,
      description='Tools to manage Astronomical Cloudy photoionization code',
      long_description=open('README.txt').read(),
      author='Christophe Morisset',
      author_email='chris.morisset@gmail.com',
      maintainer='Christophe Morisset',
      maintainer_email='chris.morisset@gmail.com',
      url='https://sites.google.com/site/cloudy3d/',
      packages=['pyCloudy','pyCloudy.c1d','pyCloudy.c3d','pyCloudy.utils', 'pyCloudy.db'],
      package_data={'pyCloudy.utils':['*txt']},
      classifiers=['Development Status :: 2 - Pre-Alpha',
                   'Intended Audience :: Science/Research',
                   'License :: Free for non-commercial use',
                   'Programming Language :: Python :: 2',
                   'Topic :: Scientific/Engineering :: Astronomy'
                   ],
      license='GPL',
      keywords="astronomy photoionization cloudy"
     )
