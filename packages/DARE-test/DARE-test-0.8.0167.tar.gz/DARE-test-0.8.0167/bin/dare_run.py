#!/usr/bin/env python
__author__ = "Sharath Maddineni"
__copyright__ = "Copyright 2011-2012, Sharath Maddineni"
__license__ = "MIT"


import sys
from dare.helpers.misc import darelogger
from dare.core.dare_manager import DareManager


def main(conffile=None):

    if (len(sys.argv) > 1):
        conffile = sys.argv[1]
    else:
        raise "missing dare configurtion file"
    darelogger.debug("using python installtion at '%s' " % sys.prefix)
    darelogger.debug("starting DARE")
    DareManager(conffile)
    darelogger.debug("DARE Exec Done")


if __name__ == "__main__" and __package__ is None:
    main()
