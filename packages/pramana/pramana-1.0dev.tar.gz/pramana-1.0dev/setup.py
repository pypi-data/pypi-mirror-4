from setuptools import setup, find_packages
import sys, os

version = '1.0'

setup(name='pramana',
      version=version,
      description="test package",
      long_description="""\
test package for python""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='test',
      author='setia pramana',
      author_email='setia.pramana@ki.se',
      url='',
      license='',
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
