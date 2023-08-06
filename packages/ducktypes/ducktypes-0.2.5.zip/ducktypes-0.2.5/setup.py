from setuptools import setup, find_packages
import sys, os

version = '0.2.5'

setup(name='ducktypes',
      version=version,
      description="behaviour based duck typing library",
      long_description=open("README").read(),
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='duck typing interfaces',
      author='Alan Franzoni',
      author_email='username@franzoni.eu',
      url='http://ducktypes.franzoni.eu',
      license='APL 2.0',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
