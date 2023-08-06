#!/usr/bin/env python
"""Asylum: The truth is, you are still inside the asylum

A library to utlize linux namespaces in python
"""

__author__ = "Da_Blitz"
__email__ = "code@pocketnix.org"
__url__ = "http://code.pocketnix.org"
__version__ = "0.4.1"
__license__ = "BSD 3 Clause"

import logging
import sys

# older versions of python (older than 2.7) dont contain some
# basic features, setup.py should specify these dependincies 
# and we manually patch them into thier normal (2.7) location 
# here
if sys.version_info < (2,7):
    import ordereddict
    import collections

    collections.OrderedDict = ordereddict.OrderedDict

    class NullHandler(logging.Handler):
        def emit(self, record):
            pass
        def handle(self, record):
            pass
        def createLock(self):
            return None
    logging.NullHandler = NullHandler

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

if __name__ == "__main__":
    # compatibility with setup.py creating the asylum cmdline app
    from asylum.utils import asylum_main
    import sys

    args = sys.argv[1:]
    sys.exit(asylum_main(args))

