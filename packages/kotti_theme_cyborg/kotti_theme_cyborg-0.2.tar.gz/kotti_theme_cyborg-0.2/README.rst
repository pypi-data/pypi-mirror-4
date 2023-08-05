==================
kotti_theme_cyborg
==================

Cyborg theme from http://bootswatch.com/cyborg/ for Kotti.

`Find out more about Kotti`_

Setup
=====

To activate the ``kotti_theme_cyborg`` theme in your Kotti site, you need to
add an entry to the ``kotti.configurators`` setting in your Paste
Deploy config.  If you don't have a ``kotti.configurators`` option,
add one.  The line in your ``[app:kotti]`` section could then look like
this::

  kotti.configurators = kotti_theme_cyborg.kotti_configure

With this, you'll be able to use TinyMCE in your Kotti site.



.. _Find out more about Kotti: http://pypi.python.org/pypi/Kotti
