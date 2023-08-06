from setuptools import setup, find_packages
import sys
import os
import oopen

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()



setup(name='oopen',
      version=oopen.__version__,
      description="Object-Oriented File and Path manipulation",
      long_description=open('README.rst', 'r').read() + "\n\n" +
                       open('HISTORY.rst', 'r').read() + "\n\n" +
                       open('LICENSE').read(),
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
      classifiers="""Development Status :: 3 - Alpha
Intended Audience :: Developers
Intended Audience :: System Administrators
License :: OSI Approved :: MIT License
Topic :: Software Development :: Libraries :: Python Modules""".split('\n'),  # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers

      )
