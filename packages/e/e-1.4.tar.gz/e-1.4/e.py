#! /usr/bin/env python

# Public domain
# Idea from Georg Brandl. Foolishly implemented by Michael Foord and Richard
# Jones
# E-mail: richard AT mechanicalcat DOT net

import os
import sys
import subprocess


def execute(arg):
    exec (compile(arg, '<cmdline>', 'single'))


def locate(arg):
    try:
        __import__(arg)
    except ImportError:
        return None

    try:
        mod = sys.modules[arg]
    except KeyError:
        print ('%s is not a valid module name' % arg)
        sys.exit(1)

    location = getattr(mod, '__file__', 'None')
    if location.endswith('.pyc'):
        location = location[:-1]
    return location


def main(args):
    if not args:
        print ('Idea from Georg Brandl. Foolishly implemented by Michael '
            'Foord and Richard Jones')
        sys.exit()

    fn = locate(args[0])
    if fn is None:
        # right, just try to execute the stuff we're
        execute(' '.join(args))
        return

    if len(args) == 1:
        print (fn)
        return

    if not fn.endswith('.py'):
        sys.exit('Module (%s) is not Python' % fn)

    prog = args[1]
    if prog == 'edit':
        prog = os.environ['EDITOR']
    elif prog == 'view':
        prog = os.environ.get('PAGER', 'less')
    sys.exit(subprocess.call(' '.join([prog, fn]), shell=True))


if __name__ == '__main__':
    main(sys.argv[1:])
