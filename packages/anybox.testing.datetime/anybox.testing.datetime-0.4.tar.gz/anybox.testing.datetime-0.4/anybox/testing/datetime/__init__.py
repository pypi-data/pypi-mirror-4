import sys
import mock_dt
sys.modules['datetime'] = mock_dt
import mock_time

sys.modules['time'] = mock_time

# registering sqlite3 adapter/converters
from . import sqlite3  # noqa
