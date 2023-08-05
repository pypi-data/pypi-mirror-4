from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='relalg',
      version=version,
      description="Relational algebra for python",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='Data, Relational Algebra, Join',
      author='Reshef Mann',
      author_email='reshef.mann@gmail.com',
      url='',
      license='BSD',
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
