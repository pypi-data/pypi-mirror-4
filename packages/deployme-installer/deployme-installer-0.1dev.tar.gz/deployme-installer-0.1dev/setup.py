from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='deployme-installer',
      version=version,
      description="Simple installer for deployme",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Rick Copeland',
      author_email='rick@arborian.com',
      url='',
      license='APACHE 2.0',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      scripts=[
        'scripts/deploy-install',
        ],
      install_requires=[
        'kajiki',
        'PyYAML',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
