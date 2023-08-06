from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='myapp',
      version=version,
      description="test",
      long_description="""\
FirstTest""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Hug',
      author_email='hug@legal.mor',
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
