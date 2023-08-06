from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='reimegardsApp',
      version=version,
      description="Reimegards App",
      long_description="""\
se short description""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='reimegard',
      author='Johan Reimegard',
      author_email='johan.reimegard@scilifelab.se',
      url='',
      license='GPLv3',
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
