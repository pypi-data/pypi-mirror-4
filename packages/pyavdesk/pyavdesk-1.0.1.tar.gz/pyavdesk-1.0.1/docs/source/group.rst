
Groups - AVDeskGroup class
==========================

pyavdesk group resource described by **AVDeskGroup** class exposes an interface to manipulate groups at server.

.. note::
    It is advised to use server resource class **AVDeskServer** as a single entry point for every server resource
    manipulation instead of direct instantiation of **AVDeskGroup** class.


Basic class usage example::

    # Setting up server connection parameters.
    av_server = pyavdesk.AVDeskServer('admin', 'password', 'http://192.168.1.70')

    # Get `Everyone` group.
    everyone = av_server.get_group(pyavdesk.META_GROUP_IDS['EVERYONE'])
    print everyone.name

    # Getting stations IDs from `Everyone`.
    # Note though that some AV-Desk versions may return an empty list here.
    stations = everyone.get_stations()
    for id in stations:
        print 'Station ID - %s' % id

    # Create a new group.
    new_group = av_server.new_group('My group.')
    new_group.save()


.. _class-group:


.. autoclass:: pyavdesk.pyavdesk.AVDeskGroup
    :members:
    :inherited-members: