
Utilities
=========

pyavdesk comes with some utility constants and functions that could be of use.


META_GROUP_IDS
--------------

META_GROUP_IDS dictionary contains identifiers for basic groups on every AV-Desk server.

Usage example::

    everyone = av_server.get_group(pyavdesk.META_GROUP_IDS['EVERYONE'])


TARIFF_IDS
----------

TARIFF_IDS dictionary contains identifiers for basic tariff groups on every AV-Desk server.

Usage example::

    tariff_classic = av_server.get_tariff(pyavdesk.TARIFF_IDS['CLASSIC'])


library_version_satisfied()
---------------------------

``library_version_satisfied()`` function tests whether version of *dwavdapi* library found in the system
is the same as version pyavdesk was designed to work with. Returns *True* if version is satisfied, otherwise *False*.


set_log_level()
---------------

``set_log_level(lvl)`` function sets module logging to a desired level and turns on log pretty formatting.
``lvl`` parameter should be logging level from  ``logging`` module. E.g.: logging.DEBUG.
