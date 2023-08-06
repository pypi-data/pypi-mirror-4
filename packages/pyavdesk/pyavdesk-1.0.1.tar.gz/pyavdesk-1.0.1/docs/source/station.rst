
Stations - AVDeskStation class
==============================

pyavdesk station resource described by **AVDeskStation** class exposes an interface to manipulate antivirus stations (PCs).

.. note::
    It is advised to use server resource class **AVDeskServer** as a single entry point for every server resource
    manipulation instead of direct instantiation of **AVDeskStation** class.


Basic class usage example::

    # Setting up server connection parameters.
    av_server = pyavdesk.AVDeskServer('admin', 'password', 'http://192.168.1.70')

    # Create a new station.
    new_station = av_server.new_station()
    new_station.save()

    # Output generated station ID.
    print new_station.id


.. _class-station:


.. autoclass:: pyavdesk.pyavdesk.AVDeskStation
    :members:
    :inherited-members:
