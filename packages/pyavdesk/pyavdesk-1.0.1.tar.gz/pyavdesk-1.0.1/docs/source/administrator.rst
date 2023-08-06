
Administrators - AVDeskAdmin class
==================================

Administrator pyavdesk resource described by **AVDeskAdmin** class exposes an interface to manipulate server administrators.

.. note::
    It is advised to use server resource class **AVDeskServer** as a single entry point for every server resource
    manipulation instead of direct instantiation of **AVDeskAdmin** class.


Basic class usage example::

    # Setting up server connection parameters.
    av_server = pyavdesk.AVDeskServer('admin', 'password', 'http://192.168.1.70')

    # Get main administrator (his login is 'admin').
    superadmin = av_server.get_administrator('admin')
    print superadmin.name

    # Create new administrator.
    new_admin = av_server.new_administrator('my_new_admin')
    new_admin.name = 'Fred'
    new_admin.last_name = 'Colon'
    new_admin.save()
    print 'Password for Fred is "%s"' % new_admin.password


.. _class-administrator:


.. autoclass:: pyavdesk.pyavdesk.AVDeskAdmin
    :members:
    :inherited-members: