======================
Statusbar for spectrwm
======================

specbar.py is a small library to use with the spectrwm_ window manager.
It has some builtin info functions and is easy extensible using the
Python decorator syntax.

.. _spectrwm: http://www.spectrwm.org

Installation
============

The simplest way to install specbar is to use pip::

    pip install specbar

Another way is to download the source and copy specbar.py somewhere in
your PYTHONPATH.

Usage
=====

Example::

    # Extending with own info function
    >>> import specbar
    >>> @specbar.info_collector(42)
    ... def get_some_info(num):
    ...     return dict(square=num**2)
    ...
    >>> specbar.loop(format_str='Square info: {square}')
    Square info: 1764
    Shutting down specbar...
    >>>

That's it now your own function get's called every 5 (default) seconds and
the format string is displayed in the statusbar. The loop (when testing) can
easily killed by pressing CTRL+C.

Using builtin functions::

    >>> import specbar
    >>> specbar.register(specbar.get_gmail_count, 'myuser', 'mysecret')
    >>> specbar.loop('New Mails: {gmail_count:<3}', 15)

Now every 15 seconds your Gmail account is checked for new mail and the
result is displayed.

Every info function must return a dict. All dicts where merged in a
defaultdict to have no exception on missing keys. See the source of
specbar.py for the returned keys of the builtin functions.

In the source distribution an example.py file is included which shows
the usage of specbar.py.

Integration with spectrwm
=========================

Create your own script or edit example.py to your needs, put it somewhere
on your PATH, make it executable (chmod +x) and add it to ~/.spectrwm.conf
as your bar_action.

Misc
====

Specbar is mainly written for spectrwm on
`Arch Linux <https://www.archlinux.org>`_ where Python 3 is the
standard Python. I think it can be used with any other window manager which
reads from stdin and with any other (posix) os which has Python 3 available.

