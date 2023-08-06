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

This isn't really designed to play well with threads, because only the
main thread will receive signals in Python. Anyway, if you're using
threads, you probably have other ways to handle timeouts.

If you want to put timeouts on static methods or class methods, you need
to put the timeout on the method first, and then decorate the wrapped
method with ``@staticmethod`` or ``@classmethod``. There are examples in
``test_pto.py``.

I am pretty sure that the lib works in Python 2.4, but I don't have an
install around to test that. If anybody wants to volunteer to verify the
lib on 2.4, please contact me.

Installation
============

To install PTO, simply::

    $ pip install pto

Or, if you absolutely must::

    $ easy_install pto

But, you really shouldn't do that.

History
=======

0.0.6 (2013-03-13)
------------------

* Add unit-testing
* Enable Travis-CI
* Add some more caveats/gotchas to README.rst
* Update sample usage
* Update trove classifiers

0.0.5 (2013-03-13)
------------------

* Include proper path for license in MANIFEST.in

0.0.4 (2013-03-13)
------------------

* Embed license on PyPI page.

0.0.3 (2013-03-13)
------------------

* First version that pip can actually install.

0.0.2 (2013-03-12)
------------------

* First draft

0.0.1 (2013-03-11)
------------------

* Conception
