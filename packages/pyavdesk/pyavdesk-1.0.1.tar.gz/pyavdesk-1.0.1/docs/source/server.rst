
Server - AVDeskServer class
===========================

Server resource is a basic resource of pyavdesk. It gives an access both to server properties (statistics, key, etc.)
and other resources manipulation means (creating and fetching server groups, tariffs, stations, etc.).

.. note::
    It is advised to use server resource class **AVDeskServer** as a single entry point for every server resource
    manipulation instead of direct instantiation of other resources classes (AVDeskGroup, AVDeskStation, etc.).


Basic class usage example::

    # Setting up server connection parameters.
    av_server = pyavdesk.AVDeskServer('admin', 'password', 'http://192.168.1.70')

    # Printing out server OS.
    info = av_server.get_info()
    print 'OS used - %s' % info['os']

    # Printing out names of tariffs available at server.
    tariffs = av_server.get_tariffs()
    for tariff in tariffs:
        print 'Tariff "%s" is available' % tariff.name

    # Getting server groups and printing out their IDs.
    groups = av_server.get_groups()
    for group in groups:
        print 'A group with ID - %s' % group.id

    # Creating a new group.
    my_group = av_server.new_group('My Group')
    my_group.save()
    print 'Server generated group ID - "%s"' % my_group.id

    # Getting server stations ID printed out.
    # Note though that some AV-Desk versions may return an empty list here.
    stations = av_server.get_stations()
    for station in stations:
        print 'Station found - %s' % station


.. _class-server:


.. autoclass:: pyavdesk.pyavdesk.AVDeskServer
    :members:
    :inherited-members:
