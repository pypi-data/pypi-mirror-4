#!/usr/bin/env python

"""
    Simply runs test_all_nonblockingloghandler's run_all.
    Due to relative imports, it can't be run as a main program, so this
    gives it the context of a package to run in.
    """

from test.test_all_nonblockingloghandler import run_all

if __name__ == '__main__':
    run_all()

