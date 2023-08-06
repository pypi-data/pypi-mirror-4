from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='reimegard',
      version=version,
      description="python course",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='python course',
      author='Johan Reimeg\xc3\xa5rd',
      author_email='johan.reimegard@scilifelab.se',
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
