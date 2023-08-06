Introduction to yara-ctypes-python
**********************************

What is yara-ctypes:

* A powerful python wrapper for `yara-project's libyara v1.6`_.
* Supports thread safe matching of YARA rules.
* namespace management to allow easy loading of multiple YARA rules into a
  single libyara context. 
* Comes with a scan module which exposes a user CLI and demonstrates a pattern
  for executing match jobs across a thread pool.


Why:

* ctypes releases the GIL on system function calls...  Run your PC to its
  true potential.
* No more building the PyC extension...  
* I found a few bugs and memory leaks and wanted to make my life simple.


As a reference and guide to yara-ctypes see: `yara-ctypes documentation`_


For additional tips / tricks with this wrapper feel free to post a question at 
the github `yara-ctypes/issues`_ page. 


Project hosting provided by `github.com`_.


[mjdorma+yara-ctypes@gmail.com]


Install and run
===============

Simply run the following::

    > python setup.py install
    > python setup.py test
    > python -m yara.scan -h

or `PyPi`_:: 

    > pip install yara
    > python -m yara.scan -h


.. note::

    If the package does not contain a pre-compiled libyara library for your
    platform you will need to build and install it. See `notes on building`_.


Compatability
=============

*yara-ctypes* is implemented to be compatible with Python 2.6+ and Python 3.x.
It has been tested against the following Python implementations:

Ubuntu 12.04:

 + CPython 2.7 (32bit, 64bit)
 + CPython 3.2 (32bit, 64bit)

Ubuntu 11.10 |build_status|:

 + CPython 2.6 (32bit)
 + CPython 2.7 (32bit)
 + CPython 3.2 (32bit)
 + PyPy 1.9.0 (32bit)

Windows 7:

 + CPython 2.6 (32bit, 64bit)
 + CPython 3.2 (32bit, 64bit)

OS X Mountain Lion

 + CPython 2.7 (64bit)


Continuous integration testing is provided by `Travis CI <http://travis-ci.org/>`_.


Issues
======

Source code for *yara-ctypes* is hosted on `GitHub <https://github.com/mjdorma/yara-ctypes>`_. 
Please file `bug reports <https://github.com/mjdorma/yara-ctypes/issues>`_
with GitHub's issues system.


Change log
==========

version 1.6.2 (28/02/2012)

* support for OS X Mountain Lion

version 1.6.1 (06/09/2012)

* Support for 64bit Windows
* Bug fixes 
* Added documentation

version 1.6.0 (01/09/2012)

* Initial release


.. _github.com: https://github.com/mjdorma/yara-ctypes
.. _PyPi: http://pypi.python.org/pypi/yara
.. _yara-ctypes/issues: https://github.com/mjdorma/yara-ctypes/issues
.. _notes on building: http://packages.python.org/yara/howto/build.html
.. _yara-ctypes documentation: http://packages.python.org/yara/
.. _yara-project's libyara v1.6: http://code.google.com/p/yara-project
.. |build_status| image:: https://secure.travis-ci.org/mjdorma/yara-ctypes.png?branch=master
   :target: http://travis-ci.org/#!/mjorma/yara-ctypes
