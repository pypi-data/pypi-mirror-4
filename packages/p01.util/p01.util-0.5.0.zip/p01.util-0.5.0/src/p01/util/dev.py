##############################################################################
#
# Copyright (c) 2012 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""Some usefull development helpers
$Id: dev.py 3099 2012-09-12 22:51:14Z roger.ineichen $
"""


import sys
import time

if sys.platform == "win32":
    # On Windows, the best timer is time.clock()
    default_timer = time.clock
else:
    # On most other platforms the best timer is time.time()
    default_timer = time.time


def printTime(_func):
    """Timer method decorator"""
    name = _func.__name__
    mod = _func.__module__
    fn = _func.__code__.co_filename
    no = _func.__code__.co_firstlineno
    def inner(inst, *args, **kws):
        _t0 = default_timer()
        res = _func(inst, *args, **kws)
        _t1 = default_timer()
        print "TIME ", fn
        print "TIME %s.%s.%s: %s" % (mod, inst.__class__.__name__, name, no)
        print "TIME ", _t1 - _t0
        return res
    return inner
