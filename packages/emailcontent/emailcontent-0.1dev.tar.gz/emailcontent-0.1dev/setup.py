from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='emailcontent',
      version=version,
      description="Functionality for extracting content from email messages.",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='email rfc822',
      author='Karel Antonio Verdecia Ortiz',
      author_email='kverdecia@uci.cu',
      url='',
      license='LGPL3',
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
