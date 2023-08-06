
Tariffs - AVDeskTariff class
============================

Tariff pyavdesk resource described by **AVDeskTariff** class exposes an interface to manipulate tariffs at server.

.. note::
    It is advised to use server resource class **AVDeskServer** as a single entry point for every server resource
    manipulation instead of direct instantiation of **AVDeskTariff** class.


Basic class usage example::

    # Setting up server connection parameters.
    av_server = pyavdesk.AVDeskServer('admin', 'password', 'http://192.168.1.70')

    # Get basic tariff.
    tariff_classic = av_server.get_tariff(pyavdesk.TARIFF_IDS['CLASSIC'])
    print tariff_classic.name

    # Create a new tariff.
    new_tariff = av_server.new_tariff('My new tariff')
    new_tariff.save()


.. _class-tariff:


.. autoclass:: pyavdesk.pyavdesk.AVDeskTariff
    :members:
    :inherited-members: