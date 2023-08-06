===========
    PTO
===========

*Easy timeouts for Python*

PTO is an MIT-licensed library to make it easy to impose time limits on
the runtime of a function that doesn't expose that functionality itself.
I was inspired by a need to prevent a scheduled job from running too
long on a platform where I was paying by the hour. Maybe you just need
to wrap a flaky network call. Either way, it's as simple as::

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

Inspiration
===========

I was inspired to do this by `Chris Wright's recipe`_. I liked the
recipe, but I got tired of copying and pasting it, and I didn't like
that the decorator didn't preserve the signature, docstring, etc.

.. _Chris Wright's recipe: http://code.activestate.com/recipes/307871-timing-out-function/

Caveats
=======

This only works on Unix-like platforms. Sorry, Windows users. I'd love
to support Windows, but the secret sauce (``signal.alarm`` from the std
lib) doesn't work on Windows.

Installation
============

To install PTO, simply::

    $ pip install pto

Or, if you absolutely must::

    $ easy_install pto

But, you really shouldn't do that.

History
=======

0.0.2 (2013-03-12)
------------------

* First draft

0.0.1 (2013-03-11)
------------------

* Conception
