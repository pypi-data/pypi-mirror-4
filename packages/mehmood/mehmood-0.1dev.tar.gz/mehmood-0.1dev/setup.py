from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='mehmood',
      version=version,
      description="Python course 2013, Scilifelab",
      long_description="""\
Python course 2013, Scilifelab""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='just testing',
      author='Mehmood Khan',
      author_email='malagori@kth.se',
      url='http://www.csc.kth.se/~malagori/',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
