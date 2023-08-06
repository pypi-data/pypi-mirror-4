# Copyright (c) 2010 Matt Harrison
from distutils.core import setup
#from setuptools import setup

from mealmakerlib import meta

setup(name='MealMaker',
      version=meta.__version__,
      author=meta.__author__,
      description='FILL IN',
      scripts=['bin/mealmaker'],
      package_dir={'mealmakerlib':'mealmakerlib'},
      packages=['mealmakerlib'],
)
