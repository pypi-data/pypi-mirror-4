======================
Hadrian.Contrib.Pomona
======================

Included in ``hadrian.contrib`` is ``hadrian.contrib.pomona`` a database driven logging module.

Setup
=====

Add ``hadrian.contrib.pomona`` to installed apps.

Usage
=====

Using the logger is as simple as importing the helper and calling this handy method::

    from hadrian.contrib.pomona.helpers import log_message
    
    log_message("This is an error message.", "Error")