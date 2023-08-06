# -*- coding: utf-8
"""
PTO is a library for adding timeout functionality to arbitrary Python functions.

Usage
=====

As a decorator
--------------

    >>> from pto import timeout
    >>> @timeout(30)
    >>> def slow_func():
    ...     while True:
    ...         pass
    ...
    >>> slow_func()
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "<string>", line 2, in foo
      File "pto.py", line 65, in _timeout
        result = f(*args, **kwargs)
      File "<stdin>", line 3, in slow_func
      File "pto.py", line 57, in handle_timeout
        raise TimedOutException
    pto.TimedOutException: u'Timed Out'

As a function
-------------

    >>> from pto import timeout
    >>> @timeout(5)
    ... def slow_func():
    ...     while True:
    ...         pass
    ...
    >>> slow_func()
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "<string>", line 2, in slow_func
      File "pto/__init__.py", line 97, in _timeout
        result = f(*args, **kwargs)
      File "<stdin>", line 3, in slow_func
      File "pto/__init__.py", line 89, in handle_timeout
        raise TimedOutException
    pto.TimedOutException: u'Timed Out'

:copyright: (c) 2013 by Hank Gay
:license: MIT, see LICENSE.txt for more details
"""
__title__ = 'PTO'
__version__ = '0.0.7'
__author__ = 'Hank Gay'
__license__ = 'MIT'
__copyright__ = 'Copyright 2013 Hank Gay'


import signal
import sys


from decorator import decorator


class TimedOutException(Exception):
    """Raised when a function times out."""
    def __init__(self, value = u"Timed Out"):
        super(TimedOutException, self).__init__()
        self.value = value

    def __str__(self):
        return repr(self.value)


def timeout(s):
    """Create decorator to time out wrapped functions after ``s`` seconds.

    :param s: number of seconds before the decorator will time out
    :rtype: decorator
    """
    def _timeout(f, *args, **kwargs):
        """A decorator that prevents ``f`` from running too long.

        :param f: the function to wrap
        :rtype: whatever ``f`` returns
        """
        def handle_timeout(signal_number, frame):
            """Handle the SIGALRM by raising a ``TimedOutException``."""
            raise TimedOutException

        # Grab a reference to the old handler.
        old = signal.signal(signal.SIGALRM, handle_timeout)

        # Start our timeout logic.
        signal.alarm(s)
        try:
            result = f(*args, **kwargs)
        finally:
            # Put the old handler back.
            old = signal.signal(signal.SIGALRM, old)
        # Wipe out any alarms that are left hanging around.
        signal.alarm(0)

        return result
    return decorator(_timeout)

