A module to allow cheating with current time in tests.
======================================================

This README is also a doctest. To it and other doctests for this package,
simply do::

   nosetests --with-doctest --doctest-extension=txt

Usage
~~~~~

Before anything, the package must be imported in order to replace the
regular ``datetime`` module with the modified one::

   >>> import anybox.testing.datetime
   >>> from datetime import datetime
   >>> import time

Let's keep the real value of ``now`` around::

   >>> start = datetime.now()
   >>> start_t = time.time()

Then you can::

   >>> datetime.set_now(datetime(2001, 01, 01, 3, 57, 0))
   >>> datetime.now()
   datetime(2001, 1, 1, 3, 57)
   >>> datetime.today()
   datetime(2001, 1, 1, 3, 57)

The time module goes along::

   >>> datetime.fromtimestamp(time.time())
   datetime(2001, 1, 1, 3, 57)

Note that you can expect a few microseconds difference (not displayed
here because ``datetime.fromtimestamp`` ignores them).


Don't forget afterwards get back to the regular system clock, otherwise
many pieces of code might get very suprised if the system clock looks as if 
it's frozen::

   >>> datetime.real_now()

Now let's check it worked::

   >>> now = datetime.now()
   >>> now > start
   True
   >>> from datetime import timedelta
   >>> now - start < timedelta(0, 0, 10000) # 10 ms
   True

And with the ``time`` module::

   >>> now_t = time.time()
   >>> now_t > start_t
   True
   >>> now_t - start_t < 0.01 # 10 ms again
   True

Other constructors are still available (this is a non regression
test)::

   >>> import datetime
   >>> datetime.time(3, 57, 0)
   datetime.time(3, 57)
   >>> datetime.datetime(2013, 1, 1, 3, 57, 0)
   datetime(2013, 1, 1, 3, 57)
   >>> datetime.date(2013, 1, 1)
   datetime.date(2013, 1, 1)

Behind the hood
~~~~~~~~~~~~~~~

Our replacement class is the one loaded from the ``datetime`` module,
but instances of the original ``datetime`` class behave exactly as
instances of our ``datetime.datetime``. This is needed because most
computational methods, actually return an object of the original
``datetime`` class. This works with python >= 2.6 only.

First let's check that our class is a subclass of the original
one. If this fails, this test does not mean anything anymore::

  >>> datetime.datetime is datetime.original_datetime
  False
  >>> issubclass(datetime.datetime, datetime.original_datetime)
  True

Then let's demonstrate the behaviour::

  >>> odt = datetime.original_datetime(2012, 1, 1)
  >>> isinstance(odt, datetime.datetime)
  True
  >>> issubclass(datetime.original_datetime, datetime.datetime)
  True

We'll need a ``tzinfo`` subclass from now on.

  >>> from datetime import tzinfo
  >>> class mytzinfo(tzinfo):
  ...     def utcoffset(self, dt):
  ...         return timedelta(hours=2)
  ...     def dst(self, dt):
  ...         return timedelta(0)

Compatibility
~~~~~~~~~~~~~

Over the lifespan of this development toolkit module, we've had to ensure
compatibility with several subsystems

SQLite
------

Also, ``sqlite3`` does recognize our ``datetime`` and ``date`` classes as
if they were the original ones::

  >>> import sqlite3
  >>> cnx = sqlite3.connect(':memory:')
  >>> cr = cnx.cursor()
  >>> cr = cr.execute("CREATE TABLE dates (dt text, d text)")
  >>> dt = datetime.datetime(2013, 1, 25, 12, 34, 0)
  >>> d = datetime.date(2013, 4, 7)
  >>> cr = cr.execute("INSERT INTO dates VALUES (?, ?)", (dt, d))
  >>> cr = cr.execute("SELECT dt, d from dates")
  >>> cr.fetchall()
  [(u'2013-01-25 12:34:00', u'2013-04-07')]

Now let's try this again with the original ones::

  >>> dt = datetime.datetime.now()
  >>> isinstance(dt, datetime.original_datetime)
  True
  >>> d = datetime.date.today()
  >>> cr = cr.execute("INSERT INTO dates VALUES (?, ?)", (dt, d))
  >>> cr = cr.execute("SELECT dt, d from dates")
  >>> res = cr.fetchall() # can't check the value, it changes a lot !
