"""Patch of time module to follow datetime.set_now

Note: monkey-patching time.time works within a module or interactive session,
but not in subsequent imports from other modules.
Replacing the whole time module by this one does work.
"""

from time import *
from time import time as original_time

from datetime import datetime

def time():
    if datetime._current_now is None:
        return original_time()
    now = datetime.now()
    return mktime(now.timetuple()) + now.microsecond / 1000000
