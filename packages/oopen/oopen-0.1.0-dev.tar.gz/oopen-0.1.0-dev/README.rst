=====
OOpen
=====

***************************************
Object-Oriented file and path handling.
***************************************

The std lib file and path options aren't very pythonic. 
I should be able to perform basic tasks directly on the file.

**Status: In development.** 

License: MIT

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

