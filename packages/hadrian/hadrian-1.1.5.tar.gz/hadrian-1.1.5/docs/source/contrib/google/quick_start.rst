======================
Hadrian.Contrib.Google
======================

Included in ``hadrian.contrib`` is ``hadrian.contrib.google`` a google analytics template tag library.

Setup
=====

Add ``hadrian.contrib.google`` to installed apps.

Usage
=====

Load the google tag library in your template::

    {% load analytics %}

Call analytics by doing so::

    {% analytics "UA-xxxxxx" %}
