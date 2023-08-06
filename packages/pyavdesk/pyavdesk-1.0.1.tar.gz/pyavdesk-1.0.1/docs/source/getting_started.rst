
Getting started with pyavdesk
=============================


Before using pyavdesk please verify that Dr.Web *dwavdapi* library is installed and available in your system.
Library installation process is beyond the scope of this documentation.

.. note::

    On Microsoft Windows systems *dwavdapi* library should reside in folder with system DLLs,
    e.g. *<DRIVE_LETTER>:\\Windows\\system32\\* for NT family systems.


Resource classes
----------------

pyavdesk interacts with AV-Desk servers by means of several classes, each of which describes a certain server resource.

* Server operations are available from :ref:`AVDeskServer <class-server>` class.
* Administrators are created and modified with the help of :ref:`AVDeskAdmin <class-administrator>` class.
* Tools for groups manipulations are available at :ref:`AVDeskGroup <class-group>` class.
* It is possible to manage server tariffs with :ref:`AVDeskTariff <class-tariff>` class.
* At last :ref:`AVDeskStation <class-station>` class introduces an interface for station control.


Quick example
-------------

:ref:`AVDeskServer <class-server>` class documentation shall be a good starting point, yet below is an example
on how to connect to server and to fetch and create some resources::


    from pyavdesk import pyavdesk

    # Check that dwavdapi library version suits pyavdesk.
    lib_satisfied, lib_version = pyavdesk.library_version_satisfied()
    if not lib_satisfied:
        print 'WARNING: System has a mismatching version of dwavdapi library - %s' % lib_version

    # Setting up server connection parameters - login, password and URL.
    av_server = pyavdesk.AVDeskServer('admin', 'password', 'http://192.168.1.70')
    # Use only trusted connections.
    av_server.verify_connection_certificate(True)

    administrators = []
    try:
        # Get a list of administrators registered on server.
        administrators = av_server.get_administrators()
    except pyavdesk.AVDeskError as e:
        print 'Unable to fetch administrators from server. Rough reason: %s' % e.message

    print 'Server has %s administrator accounts.' % len(administrators)

    # Now if there is no administrator with name `my_demo_admin` on server we'll create one.
    if 'my_demo_admin' not in [administrator.login for administrator in administrators]:

        # Creating administrator object and setting its parameters.
        demo_admin = av_server.new_administrator('my_demo_admin', 'my_demo_password')
        demo_admin.name = 'Fred'
        demo_admin.last_name = 'Colon'

        # Creating group object for future administrator to watch for.
        demo_group = av_server.new_group('Colon\'s Group')
        demo_group.description = 'This is a group lead by Fred Colon.'
        demo_group.add_emails(['fred@colon.dcw'])

        try:
            # Trying to save group.
            demo_group.save()
        except pyavdesk.AVDeskError as e:
            print 'Unable to create Fred\'s group. Reason: %s' % e.message
        else:
            # After the group has been created we link it to out administrator.
            demo_admin.add_to_groups([demo_group])

        try:
            # Trying to save administrator object.
            demo_admin.save()
        except pyavdesk.AVDeskError as e:
            print 'Unable to create Fred\'s administrator account. Reason: %s' % e.message
        else:
            print 'New administrator named %s is created. His ID is "%s". Global admin - %s. Subjected groups: %s' % \
                  (demo_admin.name, demo_admin.id, demo_admin.is_global_admin, demo_admin.get_groups())

        try:
            # Cleaning up.
            demo_admin.delete()
            demo_group.delete()
        except pyavdesk.AVDeskError:
            print 'ERROR: Unable to delete demo administrator and his group from server.'
        else:
            print 'Demo administrator and his group have been deleted from server.'

