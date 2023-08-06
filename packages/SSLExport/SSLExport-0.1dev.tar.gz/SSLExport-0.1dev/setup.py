from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='SSLExport',
      version=version,
      description="",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Rick Copeland',
      author_email='rick@synapp.io',
      url='',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'gevent'
          # -*- Extra requirements: -*-
      ],
      scripts=[
        'scripts/sslexport' ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
