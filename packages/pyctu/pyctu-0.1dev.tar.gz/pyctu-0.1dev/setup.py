from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='pyctu',
      version=version,
      description="A curses interface to configure xbees",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='xbee x-ctu',
      author='Craig Swank',
      author_email='craigswank@gmail.com',
      url='',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'pyserial'
      ],
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      pyctu=pyctu.ui:main
      xbee-update=pyctu.commands.firmware:main
      """,
      )
