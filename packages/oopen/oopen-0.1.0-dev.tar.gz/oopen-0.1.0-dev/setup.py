from setuptools import setup, find_packages
import sys, os

version = open('VERSION','r').read(-1)

setup(name='oopen',
      version=version,
      description="Object-Oriented File and Path manipulation",
      long_description=open('README.rst','r').read(-1),
      classifiers="""Development Status :: 3 - Alpha
Intended Audience :: Developers
Intended Audience :: System Administrators
License :: OSI Approved :: MIT License
Topic :: Software Development :: Libraries :: Python Modules""".split('\n'), # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='file path oo',
      author='Andrew Hekman',
      author_email='ajhekman@gmail.com',
      url='https://github.com/ajhekman/OOpen',
      license='MIT',
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
