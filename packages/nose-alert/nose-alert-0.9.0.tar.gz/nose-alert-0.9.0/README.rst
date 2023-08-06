==========
nose-watch
==========

.. image:: https://secure.travis-ci.org/lukaszb/nose-alert.png?branch=master
  :target: http://travis-ci.org/lukaszb/nose-alert

A Nose plugin that displays success/failure notification once tests are done.


Installation
============

Usual thing:

    pip install nose-watch


How to use
==========

In order to use this plugin use the ``--with-watch`` switch::

    nosetests --with-watch

If you use watchdog_ you can also run at your project's root directory::

    watchmedo shell-command -R -p "*.py" -c "nosetests --with-watch" .

This would call nose on file changes within your project.


Supported platforms
===================

Currently this plugin supports only growl_ on OS X. We are going to add support
for Linux based notifications in future (pull requests are welcomed!).


Plans
=====

Short plan is to provide a nose plugin that can show OS level notification at
tests end. Long plan, however, is to support main platforms (OS X, Linux,
Windows), eventually extract library for OS-independant notifications to
external package.

We also will try to support Python 3, this however could be somewhat problematic
- i.e. gntp_ doesn't support Python 3 yet.


Development
===========

We use tox_ for tests. Repository is at https://github.com/lukaszb/nose-watch/.
We prefer pull requests for sending patches.


Thanks
======

Thanks to Pascal Hartig, author of `nose-notify`_ for the inspiration. I have
even bluntly used images from his package.


.. _watchdog: http://pypi.python.org/pypi/watchdog
.. _tox: http://pypi.python.org/pypi/tox
.. _growl: http://growl.info/
.. _gntp: http://pypi.python.org/pypi/gntp
.. _nose-notify: https://github.com/passy/nose-notify

