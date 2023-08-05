import sys
from datetime import *
from datetime import datetime as original_datetime
from time import time as original_time
import time

class datetime(original_datetime):

    _current_now = None

    @classmethod
    def now(cls):
        now = cls._current_now
        if now is not None:
            return cls._current_now
        return original_datetime.now() # TODO adjust class

    @classmethod
    def set_now(cls, value):
        """Change the value of now.

        On may give None as a value to get back to system clock."""
        cls._current_now = value

    @classmethod
    def real_now(cls):
        """Get back to the real meaning of now.

        This should be used once the test needing to play with current
        date/time is over. Lots of other tests may fail if on a frozen value
        of 'now'.
        """
        cls.set_now(None)
