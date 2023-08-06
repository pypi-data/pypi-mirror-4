#! /usr/bin/env python
# -*- encoding: utf8 -*-

from distutils.core import setup

import e

setup(
    name="e",
    version='1.4.4',
    description='''Evaluate and display command line expressions with
        python -me expr''',
    long_description=u'\n'.join(e.__doc__.splitlines()[1:]),
    author="Georg Brandl, Michael Foord and Richard Jones",
    author_email="richard@python.org",
    py_modules=['e'],
)

# vim: set filetype=python ts=4 sw=4 et si
