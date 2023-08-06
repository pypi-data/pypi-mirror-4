js.jquery_timepicker_addon
**************************

.. contents::

Introduction
============

This library packages `jQuery-Timepicker-Addon`_ for `fanstatic`_.

.. _`fanstatic`: http://fanstatic.org
.. _`jQuery-Timepicker-Addon`: https://github.com/trentrichardson/jQuery-Timepicker-Addon

This requires integration between your web framework and ``fanstatic``,
and making sure that the original resources (shipped in the ``resources``
directory in ``js.jquery_timepicker_addon``) are published to some URL.


Hacking
=======

To minify CSS and JS after updating to a newer jQuery-Timepicker-Addon
version run::

  python2.7 bootstrap.py
  bin/buildout
  bin/minify

