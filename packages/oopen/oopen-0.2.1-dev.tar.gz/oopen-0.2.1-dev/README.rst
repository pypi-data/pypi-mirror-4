OOpen
=====
*Object-Oriented file and path handling.*



The std lib file and path options aren't very pythonic.

I should be able to perform basic tasks directly on the file.

**Status: In development.**

License: MIT

Uses `Semantic Versioning <http://semver.org/>`_

Example usage:
==============

>>> from oopen import OOpen
>>> oofile = OOpen('example_file.py')

Retrieve and set the name of a file:
------------------------------------
>>> oofile.name
'example_file.py'
>>> oofile.path
'/Users/ajhekman/Projects/oopen/oopen/example_file.py'
>>> oofile.name = 'test'
>>> oofile.path
'/Users/ajhekman/Projects/oopen/oopen/test'
>>> oofile.location
'/Users/ajhekman/Projects/oopen/oopen'

Retrieve other file information:
--------------------------------
>>> oofile.sha1
'e90296612f91b8adf498884b20c8356113c83a73'
>>> oofile.modified_time
datetime.datetime(2013, 1, 14, 9, 10, 31)



Install
-------

with pip (recommended):
+++++++++++++++++++++++
*Optional* use `virtualenv <http://pypi.python.org/pypi/virtualenv>`_:

- ``virtualenv venv``
- ``source venv/bin/activate``

``[sudo] pip install oopen``


with easy_install:
++++++++++++++++++

``sudo easy_install oopen``


from source:
++++++++++++
*update version numbers where appropriate*

`Download latest release from PyPI <http://pypi.python.org/pypi/oopen/>`_

``tar -xvzf oopen-x.x.x.tar.gz``

``cd oopen-x.x.x``

``[sudo] python setup.py install``

from git:
+++++++++
*Useful for specifying an exact commit, or for local development.*

``pip install-e git+https://github.com/ajhekman/OOpen#egg=oopen``

*you may also specify a tag or commit hash after the URL*

``pip install -e git+https://github.com/ajhekman/OOpen@0.1.1#egg=oopen``

``pip install -e git+https://github.com/ajhekman/OOpen@47f6e43cfc6391c06ae2a9eda6f63300c1b0558c#egg=oopen``


Uninstall:
----------

``pip uninstall oopen``


.. :changelog:

History
-------

0.2.1 (2013-01-23)
++++++++++++++++++

- corrected tag-version sync

0.2.0 (2013-01-23)
++++++++++++++++++

- Added preliminary support for the extension property
- Added related projects to README


0.1.3 (2013-01-20)
++++++++++++++++++

- Added publishing tasks to fabfile


0.1.2 (2013-01-20)
++++++++++++++++++

- modified .gitignore
- Improvements to fabfile
- Made reSt modifications for github
- README.rst is now a compliation of INFO,INSTALL,HISTORY,LICENSE
- Further packaging and install improvements

0.1.1 (2013-01-20)
++++++++++++++++++

- Packaging updates

0.1.0 (2013-01-19)
++++++++++++++++++

- Initial Release
- For development only, needs to be tested.

License
-------

| Copyright © 2012, 2013 Andrew Hekman
|
| Permission is hereby granted, free of charge, to any person obtaining
| a copy of this software and associated documentation files (the
| "Software"), to deal in the Software without restriction, including
| without limitation the rights to use, copy, modify, merge, publish,
| distribute, sublicense, and/or sell copies of the Software, and to
| permit persons to whom the Software is furnished to do so, subject to
| the following conditions:
|
| The above copyright notice and this permission notice shall be
| included in all copies or substantial portions of the Software.
|
| THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
| EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
| MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
| IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
| CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
| TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
| SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
