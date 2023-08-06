#! /usr/bin/env python
# -*- encoding: utf8 -*-

from distutils.core import setup

# perform the setup action
setup(
    name="e",
    version='1.4',
    description='''Evaluate and display command line expressions with
        python -me expr''',
    long_description=u"""Evaluate and display command line expressions with
``python -me expr``.

For example::

.. code:

    $ python -me 1+1
    2

Like python -c but no need for a print statement.

It allows multiple expressions::

    $ python -me 1+1 2+2
    2
    4

As a bonus, if the first argument is a module name then it will output the
location of the module source code:

.. code:

    $ python -me os
    /Library/Frameworks/Python.framework/Versions/2.6/lib/python2.6/os.py

If you follow the name of the module with a command then the module will be
opened with that command. For example, the following will open the os module
source in vim:

.. code:

    $ python -me os vim

The "e" module recognises the special command names "edit" and "view" which
will result in it looking up your editor and viewer commands in the
environment variables $EDITOR and $PAGER respectively. The latter defaults to
"less". This is only just slightly easier than writing, for example:

.. code:

    $ vim `python -me os`
""",
    author="Georg Brandl, Michael Foord and Richard Jones",
    author_email="richard@python.org",
    scripts=['e.py'],
)

# vim: set filetype=python ts=4 sw=4 et si
