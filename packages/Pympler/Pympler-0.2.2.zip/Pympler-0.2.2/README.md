README for pympler
==================


Before installing Pympler, try it with your Python version:

    python setup.py try

If any errors are reported, check whether your Python version is
supported by all the Pympler modules. Pympler is written entirely in
Python, with no dependencies other than standard Python modules and
libraries.  All Pympler modules work with Python 2.5, 2.6, 2.7, 3.1
and 3.2.

Installation

1. Build the Pympler package:

    python setup.py build

2.a) For a system-wide installation run:

    python setup.py install

2.b) For a user-specific** installation run:

    python setup.py --user install

3) Test the installed Pympler package:

    python setup.py test


**) Note, the user-specific installation requires
    Python 2.6 or higher.


Usage
-----
The usage of pympler is described in the documentation.  It is
available either in this distribution at *doc/index.html* or
you can [read it online](http://packages.python.org/Pympler/).


Contributing
------------
You can post wishes, bug reports or patches at our
[issue tracker](https://github.com/pympler/pympler/issues) or
write an email to *pympler-dev@googlegroups.com*.


[![Build status](https://secure.travis-ci.org/pympler/pympler.png?branch=master)](http://travis-ci.org/pympler/pympler)
