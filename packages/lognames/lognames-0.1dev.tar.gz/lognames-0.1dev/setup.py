from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='lognames',
      version=version,
      description="This is a package that uses logging to print the arguments and name of the method called",
      long_description="""\
This is a package that uses logging to print the arguments and name of the method called""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='logging method name',
      author='Xian Jacobs',
      author_email='cricobs@gmail.com',
      url='http://stackoverflow.com/users/1006989/x-jacobs',
      license='GPL',
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
