A module to allow playing with time in tests.

This README is also a doctest. To it and other doctests for this package,
simply do::

   nosetests --with-doctest --doctest-extension=txt


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
