###############################################################################
#
# Copyright 2012 by CipherHealth, LLC
#
###############################################################################
"""
Shared helpers used by the test suite.
"""

import logging
import sys
import time


class StdoutHandler(logging.StreamHandler):
    """Logging handler that logs to the current binding of sys.stdout"""

    @property
    def stream(self):
        return sys.stdout

    def __init__(self):
        # skip StreamHandler.__init__
        logging.Handler.__init__(self)


def setUpLogging(log):
    handler = StdoutHandler()
    handler._old_propagate = log.propagate
    handler._old_level = log.level
    log.propagate = False
    log.setLevel(logging.DEBUG)
    log.addHandler(handler)


def tearDownLogging(log):
    for handler in log.handlers:
        if isinstance(handler, StdoutHandler):
            log.propagate = handler._old_propagate
            log.level = handler._old_level
            log.handlers.remove(handler)
            return


def setUpFrozenTime():
    orig_time = time.time
    time.time = lambda: 1354719320
    time.time._orig_time = orig_time


def tearDownFrozenTime():
    time.time = getattr(time.time, '_orig_time', time.time)

