# -*- coding: utf-8 -*-

###
#
# Copyright (c) 2003-2013, Doctor Web, Ltd.
#
# Following code is the property of Doctor Web, Ltd.
# Distributed under the license available from LICENSE file provided
# with the source code.
#
# Dr.Web is a registered trademark of Doctor Web, Ltd.
#
# http://www.drweb.com
# http://www.av-desk.com
#
###

try:
    from pyavdesk import pyavdesk
except ImportError:
    import pyavdesk

import unittest
import datetime
from os import path

'''Note that these tests should pass on Python 2.6+ distributions.'''

AVDESK = pyavdesk.AVDeskServer('testmaster', 'password', 'http://192.168.10.116', connection_timeout=3)
TEST_GROUP_ID = 'test_grp'
TEST_STATION_ID = 'test_av'

#AVDESK.switch_to_debug_mode()
#import logging
#pyavdesk.set_log_level(logging.DEBUG)


def get_microtime():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")


def wipe_test_data():
    """Wipes stale pyavdesk test data from server."""

    def cleaner(obj_list, search_field='name', move_to=None):
        for item in obj_list:
            print ('%s ID: %s' % (item.__class__.__name__, item.id))
            item.retrieve_info()
            field = getattr(item, search_field)
            print ('%s: %s' % (search_field.capitalize(), field))

            if 'pyavdesk' in field:
                try:
                    if move_to is not None:
                        item.delete(move_to)
                    else:
                        item.delete()
                except pyavdesk.AVDeskServerError as e:
                    print (' *** Error: %s' % e)
                    pass

            print ('')
            print ('===' * 20)
            print ('')

    cleaner(AVDESK.get_administrators(), 'login')
    cleaner(AVDESK.get_groups())
    cleaner(AVDESK.get_stations(False))
    cleaner(AVDESK.get_tariffs(), move_to=pyavdesk.TARIFF_IDS['CLASSIC'])


class CommonFunctionsCheck(unittest.TestCase):

    def test_handle(self):
        self.assertTrue(pyavdesk.library_version_satisfied()[0])
        pyavdesk.LIBRARY_EXPECTED_VERSION = 'unthinkable'
        self.assertFalse(pyavdesk.library_version_satisfied()[0])

        pyavdesk.API_LIB = None
        self.assertRaises(pyavdesk.AVDeskError, pyavdesk.library_version_satisfied)


class AVDeskServerCheck(unittest.TestCase):

    def test_handle(self):
        self.assertEquals(AVDESK._handle is None, False)

    def test_verify_connection_certificate(self):
        self.assertEquals(AVDESK.verify_connection_certificate(True) is None, True)
        self.assertEquals(AVDESK.verify_connection_certificate(False) is None, True)
        self.assertRaises(pyavdesk.AVDeskError, AVDESK.verify_connection_certificate, True, certificate_path='no-such-path')
        self.assertEquals(AVDESK.verify_connection_certificate(True, path.abspath(__file__)) is None, True)

    def test_debug_mode(self):
        self.assertTrue(AVDESK.switch_to_debug_mode())

    def test_user_agent(self):
        self.assertTrue(AVDESK.set_user_agent('pyavdesk agent'))

    def test_run_task(self):
        self.assertRaises(pyavdesk.AVDeskServerError, AVDESK.run_task, 'nonexistent_task')
        self.assertEquals(AVDESK.run_task('scc_unknown_stations'), True)

    def test_resource_name(self):
        self.assertEqual(AVDESK._resource_name, 'srv')

    def test_connector(self):
        self.assertEqual(AVDESK._connector, AVDESK)

    def test_server_info(self):
        info = AVDESK.get_info()
        self.assertEquals(isinstance(info, dict), True)
        self.assertEquals(isinstance(info['uuid'], str), True)
        self.assertEquals(isinstance(info['uptime'], long), True)

    def test_key_info(self):
        info = AVDESK.get_key_info()
        self.assertEquals(isinstance(info, dict), True)
        self.assertEquals(isinstance(info['uuid'], str), True)
        self.assertEquals(isinstance(info['user'], long), True)

    def test_statistics(self):
        info = AVDESK.get_statistics()
        self.assertEquals(isinstance(info, dict), True)
        self.assertEquals(isinstance(info['groups_total'], long), True)

    def test_init_group_new(self):
        group = AVDESK.new_group('Test pyavdesk group')
        self.assertEquals(isinstance(group, pyavdesk.AVDeskGroup), True)

    def test_new_group_with_parent(self):
        parent_group = AVDESK.new_group('Test pyavdesk parent group')
        self.assertEquals(isinstance(parent_group, pyavdesk.AVDeskGroup), True)
        parent_group.save()
        self.assertEquals(parent_group.id is None, False)

        group = AVDESK.new_group('Test pyavdesk group', parent_group=parent_group)
        self.assertEquals(isinstance(group, pyavdesk.AVDeskGroup), True)
        group.save()
        self.assertEqual(group.parent, parent_group.id)
        
        group.delete()
        parent_group.delete()

    def test_init_tariff_new(self):
        tariff = AVDESK.new_tariff('Test pyavdesk tariff')
        self.assertEquals(isinstance(tariff, pyavdesk.AVDeskTariff), True)

    def test_new_tariff_with_parent(self):
        parent_tariff = AVDESK.new_tariff('Test pyavdesk parent tariff')
        self.assertEquals(isinstance(parent_tariff, pyavdesk.AVDeskTariff), True)
        parent_tariff.save()
        self.assertEquals(parent_tariff.id is None, False)

        tariff = AVDESK.new_tariff('Test pyavdesk tariff', parent_tariff=parent_tariff)
        self.assertEquals(isinstance(tariff, pyavdesk.AVDeskTariff), True)
        tariff.save()
        self.assertEqual(tariff.parent, parent_tariff.id)

        tariff.delete()
        parent_tariff.delete()

    def test_init_station_new(self):
        station = AVDESK.new_station()
        self.assertEquals(isinstance(station, pyavdesk.AVDeskStation), True)

    def test_new_station_with_parents(self):
        tariff = AVDESK.new_tariff('Test pyavdesk tariff')
        self.assertEquals(isinstance(tariff, pyavdesk.AVDeskTariff), True)
        tariff.save()
        self.assertEquals(tariff.id is None, False)

        parent_group = AVDESK.new_group('Test pyavdesk parent group')
        self.assertEquals(isinstance(parent_group, pyavdesk.AVDeskGroup), True)
        parent_group.save()
        self.assertEquals(parent_group.id is None, False)

        station = AVDESK.new_station(parent_group=parent_group, tariff=tariff)
        self.assertEquals(isinstance(station, pyavdesk.AVDeskStation), True)
        station.save()
        self.assertEqual(station.tariff, tariff.id)
        self.assertEqual(parent_group.id, station.parent)

        station.delete()
        parent_group.delete()
        self.assertRaises(pyavdesk.AVDeskServerError, tariff.delete)

    def test_get_groups(self):
        groups = AVDESK.get_groups()
        self.assertEquals(isinstance(groups, list), True)
        count = len(groups)
        self.assertEquals(count >= 0, True)
        if count > 0 :
            self.assertEquals(isinstance(groups[0].get_id(), str), True)
            self.assertEquals(isinstance(groups[0].get_name(), str), True)

    def test_get_repositories(self):
        repositories = AVDESK.get_repositories()
        self.assertEquals(isinstance(repositories, list), True)
        count = len(repositories)
        self.assertEquals(count >= 0, True)
        self.assertEquals(isinstance(repositories[0], dict), True)
        self.assertEquals(isinstance(repositories[0]['name'], str), True)
        self.assertEquals(isinstance(repositories[0]['code'], str), True)


class AVDeskGroupTariffCheck(unittest.TestCase):

    def setUp(self):
        self.obj = pyavdesk.AVDeskTariff(AVDESK)
        self.title = 'Тестовая pyavdesk тарифная группа (%s)' % get_microtime()
        self.descr = 'This tariff group is created by pyavdesk test script. If it is not removed automatically, that means that something went wrong.'
        self.descr_alt = 'This tariff group is updated by pyavdesk test script. If it is not removed automatically, that means that something weird has happened.'

    def test_set_av_component(self):
        self.obj.name = self.title
        self.obj.set_av_component(pyavdesk.AV_COMPONENT_IDS['FIREWALL'], pyavdesk.AV_COMPONENT_STATES['DISABLED'])
        self.obj.set_av_component(pyavdesk.AV_COMPONENT_IDS['SCANNER_32W'])
        self.obj.set_av_component(pyavdesk.AV_COMPONENT_IDS['SPIDERGATE'], pyavdesk.AV_COMPONENT_STATES['REQUIRED'])
        self.obj.save()

        components = self.obj.get_av_components()
        self.obj.delete()

        components = dict((component['code'], component['status']) for component in components)
        # Firewall
        self.assertEqual(components[105], 0)
        # Scanner
        self.assertEqual(components[4], 1)
        # SpiderGate
        self.assertEqual(components[38], 2)

    def test_get_av_components(self):
        basic_tariff = pyavdesk.AVDeskTariff(AVDESK, pyavdesk.TARIFF_IDS['CLASSIC'])
        components = basic_tariff.get_av_components()
        self.assertEquals(isinstance(components, list), True)
        self.assertEquals(isinstance(components[0], dict), True)

    def test_add_station(self):
        station = AVDESK.new_station()

        self.obj.name = self.title
        self.obj.add_station(station)
        tariff_id = self.obj.get_id()
        station_tariff_id = station.get_tariff()

        station.delete()
        self.assertRaises(pyavdesk.AVDeskServerError, self.obj.delete)

        self.assertEqual(tariff_id, station_tariff_id)

    def test_save(self):
        self.obj.name = self.title
        self.obj.description = self.descr
        created = self.obj.save()
        self.assertTrue(created)
        self.assertEqual(self.obj.name, self.title)
        self.assertEqual(self.obj.description, self.descr)

        self.obj.description = self.descr_alt
        updated = self.obj.save()
        self.assertTrue(updated)
        self.assertEqual(self.obj.name, self.title)
        self.assertEqual(self.obj.description, self.descr_alt)

        deleted = self.obj.delete()
        self.assertTrue(deleted)

    def test_handle(self):
        self.assertEquals(self.obj._handle is None, False)

    def test_resource_name(self):
        self.assertEqual(self.obj._resource_name, 'group')

    def test_connector(self):
        self.assertEqual(self.obj._connector, AVDESK)

    def test_get_statistics(self):
        self.assertRaises(NotImplementedError, self.obj.send_message)

    def test_send_message(self):
        self.assertRaises(NotImplementedError, self.obj.send_message)

    def test_get_time_created_modified(self):
        self.assertEquals(self.obj.get_time_created()is None, True)
        self.assertEquals(self.obj.get_time_modified() is None, True)

        self.obj.name = self.title
        self.obj.description = self.descr
        self.obj.create()
        created = self.obj.get_time_created()
        modified = self.obj.get_time_modified()
        self.obj.delete()
        self.assertEquals(created is None, False)
        self.assertEquals(modified is None, False)

    def test_parent_set_get(self):
        self.assertEquals(self.obj.get_parent() is None, True)
        self.assertEquals(self.obj.get_parent(False) is None, True)

        new_parent_group = pyavdesk.AVDeskTariff(AVDESK)
        new_parent_group.name = self.title
        new_parent_group.create()

        self.obj.name = self.title
        self.obj.set_parent(new_parent_group)
        self.obj.create()
        self.assertEqual(self.obj.get_parent(), new_parent_group.id)

        self.obj.delete()
        new_parent_group.delete()

    def test_create_update_delete(self):
        self.obj.name = self.title
        self.obj.description = self.descr
        result = self.obj.create()

        self.assertEqual(result, True)
        self.assertEquals(self.obj.id is None, False)
        self.assertEqual(self.obj.name,  self.title)

        new_description = self.descr_alt
        self.obj.description = new_description
        result = self.obj.update()
        self.assertEqual(result, True)
        self.assertEqual(self.obj.description,  new_description)

        result = self.obj.delete()
        self.assertEqual(result, True)

    def test_set_id(self):
        self.obj.set_id('test_tariff_group')
        self.assertEqual(self.obj.get_id(), 'test_tariff_group')

    def test_get_id(self):
        self.assertEquals(self.obj.get_id() is None, True)

    def test_set_name(self):
        self.obj.set_name('test_tariff_name')
        self.assertEqual(self.obj.get_name(), 'test_tariff_name')

    def test_get_name(self):
        self.assertEquals(self.obj.get_name() is None, True)

    def test_set_description(self):
        self.obj.set_description('test_tariff_descr')
        self.assertEqual(self.obj.get_description(), 'test_tariff_descr')

    def test_get_description(self):
        self.assertEquals(self.obj.get_description() is None, True)

    def test_grace_period_set_get(self):
        self.assertEquals(self.obj.get_grace_period() is None, True)
        self.obj.name = self.title
        self.obj.grace_period = 10
        self.obj.create()
        period = self.obj.get_grace_period()
        self.obj.delete()
        self.assertEqual(period, 10)


class AVDeskGroupCheck(unittest.TestCase):

    def setUp(self):
        self.obj = pyavdesk.AVDeskGroup(AVDESK)
        self.title = 'Тестовая pyavdesk группа (%s)' % get_microtime()
        self.descr = 'This group is created by pyavdesk test script. If it is not removed automatically, that means that something went wrong.'
        self.descr_alt = 'This group is updated by pyavdesk test script. If it is not removed automatically, that means that something weird has happened.'

    def test_type_categories(self):
        self.obj.name = self.title
        self.obj.save()
        self.assertTrue(self.obj.is_custom)
        self.assertFalse(self.obj.is_platform)
        self.assertFalse(self.obj.is_status)
        self.assertFalse(self.obj.is_system)
        self.assertFalse(self.obj.is_tariff)
        self.assertFalse(self.obj.is_transport)
        self.assertFalse(self.obj.is_virtual)
        self.obj.delete()

        group = pyavdesk.AVDeskGroup(AVDESK, pyavdesk.META_GROUP_IDS['EVERYONE'])
        self.assertFalse(group.is_custom)
        self.assertFalse(group.is_platform)
        self.assertFalse(group.is_status)
        self.assertTrue(group.is_system)
        self.assertFalse(group.is_tariff)
        self.assertFalse(group.is_transport)
        self.assertFalse(group.is_virtual)

        group = pyavdesk.AVDeskGroup(AVDESK, pyavdesk.META_GROUP_IDS['PLATFORM'])
        self.assertFalse(group.is_custom)
        self.assertFalse(group.is_platform)
        self.assertFalse(group.is_status)
        self.assertFalse(group.is_system)
        self.assertFalse(group.is_tariff)
        self.assertFalse(group.is_transport)
        self.assertTrue(group.is_virtual)

    def test_add_station(self):
        station = AVDESK.new_station()

        self.obj.name = self.title
        self.obj.add_station(station)
        group_id = self.obj.get_id()
        station_groups = station.get_groups()

        station.delete()
        self.obj.delete()

        self.assertTrue(len(station_groups)==1)
        self.assertEquals(group_id in station_groups, True)

    def test_save(self):
        self.obj.name = self.title
        self.obj.description = self.descr
        created = self.obj.save()
        self.assertTrue(created)
        self.assertEqual(self.obj.name, self.title)
        self.assertEqual(self.obj.description, self.descr)

        self.obj.description = self.descr_alt
        updated = self.obj.save()
        self.assertTrue(updated)
        self.assertEqual(self.obj.name, self.title)
        self.assertEqual(self.obj.description, self.descr_alt)

        deleted = self.obj.delete()
        self.assertTrue(deleted)

    def test_handle(self):
        self.assertEquals(self.obj._handle is None, False)

    def test_resource_name(self):
        self.assertEqual(self.obj._resource_name, 'group')

    def test_connector(self):
        self.assertEqual(self.obj._connector, AVDESK)

    def test_get_children(self):
        self.assertEquals(self.obj.get_subgroups() >= 0, True)

    def test_get_stations(self):
        self.assertEquals(self.obj.get_stations() >= 0, True)

    def test_get_id(self):
        self.assertEquals(self.obj.get_id() is None, True)

    def test_get_name(self):
        self.assertEquals(self.obj.get_name() is None, True)

    def test_statistics(self):
        self.assertEquals(self.obj.get_statistics() is None, True)

        self.obj.name = self.title
        self.obj.create()
        stats = self.obj.get_statistics()
        self.assertEquals(isinstance(stats, dict), True)
        self.obj.delete()

    def test_send_message(self):
        self.assertFalse(self.obj.send_message('Message to nowhere.'))
        
        self.obj.name = self.title
        self.obj.create()
        self.assertTrue(self.obj.send_message('This is a test message from pyavdesk to a group.'))
        self.obj.delete()

    def test_get_time_created_modified(self):
        self.assertEquals(self.obj.get_time_created() is None, True)
        self.assertEquals(self.obj.get_time_modified() is None, True)

        self.obj.name = self.title
        self.obj.description = self.descr
        self.obj.create()
        created = self.obj.get_time_created()
        modified = self.obj.get_time_modified()
        self.obj.delete()
        self.assertEquals(created is None, False)
        self.assertEquals(modified is None, False)

    def test_get_key(self):
        self.assertEquals(self.obj.get_key() is None, True)

        test_group = AVDESK.get_group(TEST_GROUP_ID)
        key = test_group.get_key()
        self.assertEquals(key is None, False)
        self.assertEquals(key['inherited_group_id'] is None, False)
        self.assertEquals(key['key'] is None, False)
        self.assertEqual(key['key'][0], '=')

    def test_parent_set_get(self):
        self.assertEquals(self.obj.get_parent() is None, True)
        self.assertEquals(self.obj.get_parent(False) is None, True)

        new_parent_group = pyavdesk.AVDeskGroup(AVDESK)
        new_parent_group.name = self.title
        new_parent_group.create()

        self.obj.name = self.title
        self.obj.set_parent(new_parent_group)
        self.obj.create()
        self.assertEqual(self.obj.get_parent(), new_parent_group.id)

        self.obj.delete()
        new_parent_group.delete()

    def test_set_id(self):
        self.obj.set_id('test_group')
        self.assertEqual(self.obj.get_id(), 'test_group')

    def test_set_name(self):
        self.obj.set_name('test_group_name')
        self.assertEqual(self.obj.get_name(), 'test_group_name')

    def test_description_get_set(self):
        self.assertEquals(self.obj.get_description() is None, True)
        self.obj.set_description('test_group_descr')
        self.assertEqual(self.obj.get_description(), 'test_group_descr')

    def test_create_update_delete(self):
        self.obj.name = self.title
        self.obj.description = self.descr
        result = self.obj.create()

        self.assertEqual(result, True)
        self.assertEquals(self.obj.id is None, False)
        self.assertEqual(self.obj.name,  self.title)

        new_description = self.descr_alt
        self.obj.description = new_description
        result = self.obj.update()
        self.assertEqual(result, True)
        self.assertEqual(self.obj.description,  new_description)

        result = self.obj.delete()
        self.assertEqual(result, True)

    def test_emails(self):
        emails = ['one@bingo.mm', 'two@bingo.mm', 'three@bingo.mm']
        self.obj.name = self.title
        self.obj.description = self.descr

        self.assertEqual(self.obj.get_emails(), [])

        self.obj.add_emails(emails)
        self.assertEqual(self.obj.get_emails(), emails)

        self.obj.delete_emails(['one@bingo.mm', 'two@bingo.mm'])
        self.assertEqual(self.obj.get_emails(), ['three@bingo.mm'])


class AVDeskStationCheck(unittest.TestCase):

    def setUp(self):
        self.obj = pyavdesk.AVDeskStation(AVDESK)
        self.title = 'Тестовая pyavdesk станция (%s)' % get_microtime()
        self.descr = 'This station is created by pyavdesk test script. If it is not removed automatically, that means that something went wrong.'
        self.descr_alt = 'This station is updated by pyavdesk test script. If it is not removed automatically, that means that something weird has happened.'

    def test_get_av_components(self):
        components = self.obj.get_av_components()
        self.assertEquals(isinstance(components, list), True)
        self.assertEqual(len(components), 0)

        self.obj.name = self.title
        self.obj.save()
        components = self.obj.get_av_components()
        self.obj.delete()

        self.assertEquals(isinstance(components, list), True)
        self.assertEquals(len(components) > 0, True)
        self.assertEquals(isinstance(components[0], dict), True)

    def test_get_av_modules(self):
        modules = self.obj.get_av_modules()
        self.assertEquals(isinstance(modules, list), True)
        self.assertEqual(len(modules), 0)

        self.obj.name = self.title
        self.obj.save()
        modules = self.obj.get_av_modules()
        self.obj.delete()

        self.assertEquals(isinstance(modules, list), True)
        self.assertEqual(len(modules), 0)

    def test_get_av_components_installed(self):
        components = self.obj.get_av_components_installed()
        self.assertEquals(isinstance(components, list), True)
        self.assertEqual(len(components), 0)

        self.obj.name = self.title
        self.obj.save()
        components = self.obj.get_av_components_installed()
        self.obj.delete()

        self.assertEquals(isinstance(components, list), True)
        self.assertEqual(len(components), 0)

    def test_get_av_components_running(self):
        components = self.obj.get_av_components_running()
        self.assertEquals(isinstance(components, list), True)
        self.assertEqual(len(components), 0)

        self.obj.name = self.title
        self.obj.save()
        components = self.obj.get_av_components_running()
        self.obj.delete()

        self.assertEquals(isinstance(components, list), True)
        self.assertEqual(len(components), 0)

    def test_get_av_bases(self):
        self.obj.name = self.title
        self.obj.save()
        self.assertEqual(len(self.obj.get_av_bases()), 0)

        try:
            station = AVDESK.get_station('test_av')
        except pyavdesk.AVDeskError:
            pass
        else:
            bases = station.get_av_bases()
            self.assertEquals(isinstance(bases, list), True)
            if 0 in bases:
                self.assertEquals(isinstance(bases[0], dict), True)

    def test_get_av_packages(self):
        self.obj.name = self.title
        self.assertEqual(len(self.obj.get_av_packages()), 0)
        self.obj.save()
        self.assertNotEquals(len(self.obj.get_av_packages()), 0)

        try:
            station = AVDESK.get_station('test_av')
        except pyavdesk.AVDeskError:
            pass
        else:
            packages = station.get_av_packages()
            self.assertEquals(isinstance(packages, list), True)
            if 0 in packages:
                self.assertEquals(isinstance(packages[0], dict), True)

    def test_get_history(self):
        self.assertEqual(self.obj.get_history(), [])

        try:
            station = AVDESK.get_station('test_av')
        except pyavdesk.AVDeskError:
            pass
        else:
            history = station.get_history()
            self.assertEquals(isinstance(history, list), True)
            self.assertEquals(isinstance(history[0], dict), True)

    def test_save(self):
        self.obj.name = self.title
        self.obj.description = self.descr
        created = self.obj.save()
        self.assertTrue(created)
        self.assertEqual(self.obj.name, self.title)
        self.assertEqual(self.obj.description, self.descr)

        self.obj.description = self.descr_alt
        updated = self.obj.save()
        self.assertTrue(updated)
        self.assertEqual(self.obj.name, self.title)
        self.assertEqual(self.obj.description, self.descr_alt)

        deleted = self.obj.delete()
        self.assertTrue(deleted)

    def test_handle(self):
        self.assertEquals(self.obj._handle is None, False)

    def test_resource_name(self):
        self.assertEqual(self.obj._resource_name, 'station')

    def test_connector(self):
        self.assertEqual(self.obj._connector, AVDESK)

    def test_send_message(self):
        self.assertFalse(self.obj.send_message('Message to nowhere.'))

        self.obj.name = self.title
        self.obj.create()
        self.assertTrue(self.obj.send_message('This is a test message from pyavdesk to the station.'))
        self.obj.delete()

    def test_get_time_created_modified(self):
        self.assertEquals(self.obj.get_time_created() is None, True)
        self.assertEquals(self.obj.get_time_modified() is None, True)

        self.obj.name = self.title
        self.obj.description = self.descr
        self.obj.create()
        created = self.obj.get_time_created()
        modified = self.obj.get_time_modified()
        self.obj.delete()
        self.assertEquals(created is None, False)
        self.assertEquals(modified is None, False)

    def test_get_key(self):
        self.assertEquals(self.obj.get_key() is None, True)

        test_station = AVDESK.get_station(TEST_STATION_ID)
        key = test_station.get_key()
        self.assertEquals(key is None, False)
        self.assertEquals(key['inherited_group_id'] is None, False)
        self.assertEquals(key['key'] is None, False)
        self.assertEqual(key['key'][0], '=')

    def test_parent_set_get(self):
        self.assertEquals(self.obj.get_parent() is None, True)
        self.assertEquals(self.obj.get_parent(False) is None, True)

        new_parent_group = pyavdesk.AVDeskGroup(AVDESK)
        new_parent_group.name = self.title
        new_parent_group.create()

        self.obj.name = self.title
        self.obj.set_parent(new_parent_group)
        self.obj.create()
        self.assertEqual(self.obj.get_parent(), new_parent_group.id)

        self.obj.delete()
        new_parent_group.delete()

    def test_create_update_delete(self):
        self.obj.name = self.title
        self.obj.description = self.descr
        result = self.obj.create()

        self.assertEqual(result, True)
        self.assertEquals(self.obj.id is None, False)
        self.assertEqual(self.obj.name,  self.title)

        new_description = self.descr_alt
        self.obj.description = new_description
        result = self.obj.update()
        self.assertEqual(result, True)
        self.assertEqual(self.obj.description,  new_description)

        result = self.obj.delete()
        self.assertEqual(result, True)

    def test_emails(self):
        emails = ['one@bingo.mm', 'two@bingo.mm', 'three@bingo.mm']
        self.obj.name = self.title
        self.obj.description = self.descr

        self.assertEqual(self.obj.get_emails(), [])

        self.obj.add_emails(emails)
        self.assertEqual(self.obj.get_emails(), emails)

        self.obj.delete_emails(['one@bingo.mm', 'two@bingo.mm'])
        self.assertEqual(self.obj.get_emails(), ['three@bingo.mm'])

    def test_set_id(self):
        self.obj.set_id('test_station')
        self.assertEqual(self.obj.get_id(), 'test_station')

    def test_get_id(self):
        self.assertEquals(self.obj.get_id() is None, True)

    def test_set_name(self):
        self.obj.set_name('test_station_name')
        self.assertEqual(self.obj.get_name(), 'test_station_name')

    def test_get_name(self):
        self.assertEquals(self.obj.get_name() is None, True)

    def test_set_description(self):
        self.obj.set_description('test_station_descr')
        self.assertEqual(self.obj.get_description(), 'test_station_descr')

    def test_get_description(self):
        self.assertEquals(self.obj.get_description() is None, True)

    def test_statistics(self):
        self.assertEquals(self.obj.get_statistics() is None, True)

        self.obj.name = self.title
        self.obj.create()
        stats = self.obj.get_statistics()
        self.assertEquals(isinstance(stats, dict), True)
        self.obj.delete()

    def test_place_data(self):
        self.assertEquals(isinstance(self.obj.get_place_data(), dict), True)

        self.obj.name = self.title
        args = {
            'country': 643,
            'latitude': 123456,
            'longitude': 123456,
            'province': 'pyavdesk province',
            'city': 'pyavdesk city',
            'street': 'pyavdesk street',
            'organization': 'pyavdesk organization',
            'department': 'pyavdesk department',
            'floor': 'pyavdesk floor',
            'room': 'pyavdesk room',
        }
        self.obj.set_place_data(**args)
        self.assertEqual(self.obj.get_place_data(), args)

        self.obj.create()
        data = self.obj.get_place_data()
        self.obj.delete()

        self.assertEqual(data, args)

    def test_get_os(self):
        self.assertEqual(self.obj.get_os(), '<unknown>')

        self.obj.name = self.title
        self.obj.create()
        os = self.obj.get_os()
        self.obj.delete()

        self.assertEquals(os is None, False)
        self.assertEquals(isinstance(os, str), True)

    def test_get_state(self):
        self.assertEqual(self.obj.get_state(), '<unknown>')
        self.assertEqual(self.obj.get_state(True), pyavdesk.VAR_UINITIALIZED_NUM)

        self.obj.name = self.title
        self.obj.create()
        state = self.obj.get_state()
        state_id = self.obj.get_state(True)
        self.obj.delete()

        self.assertEquals(state is None, False)
        self.assertEquals(state_id is None, False)
        self.assertEquals(isinstance(state, str), True)
        self.assertEquals(isinstance(state_id, int), True)

    def test_get_download_url(self):
        self.assertEquals(self.obj.get_download_url() is None, True)

        self.obj.name = self.title
        self.obj.create()
        url = self.obj.get_download_url()
        self.obj.delete()

        self.assertEquals(url is None, False)
        self.assertEquals(isinstance(url, str), True)

    def test_get_config_url(self):
        self.assertEquals(self.obj.get_config_url() is None, True)

        self.obj.name = self.title
        self.obj.create()
        url = self.obj.get_config_url()
        self.obj.delete()

        self.assertEquals(url is None, False)
        self.assertEquals(isinstance(url, str), True)

    def test_password_get_set(self):
        self.assertEquals(self.obj.get_password() is None, True)

        self.obj.name = self.title
        self.obj.set_password('pyavdeskpasswD123')
        self.obj.create()

        password = self.obj.get_password()
        self.obj.delete()

        self.assertEqual(password, 'pyavdeskpasswD123')

    def test_tariff_get_set(self):
        self.assertEquals(self.obj.get_tariff() is None, True)

        tariff_group = pyavdesk.AVDeskTariff(AVDESK)
        tariff_group.set_name('Test pyavdesk tariff')
        tariff_group.create()
        tariff_group_id = tariff_group.get_id()

        self.obj.name = self.title
        self.obj.set_tariff(tariff_group)
        self.obj.create()

        tariff_id = self.obj.get_tariff()
        self.obj.delete()
        self.assertRaises(pyavdesk.AVDeskServerError, tariff_group.delete)

        self.assertEqual(tariff_id, tariff_group_id)

    def test_grace_period(self):
        self.assertEquals(self.obj.get_grace_period() is None, True)

        tariff_group = pyavdesk.AVDeskTariff(AVDESK)
        tariff_group.set_name('Test pyavdesk tariff')
        self.assertRaises(pyavdesk.AVDeskError, tariff_group.set_grace_period, 133)
        tariff_group.set_grace_period(33)
        tariff_group.create()

        self.obj.name = self.title
        self.obj.set_tariff(tariff_group)
        self.obj.create()
        grace_period = self.obj.get_grace_period()
        self.obj.delete()

        self.assertRaises(pyavdesk.AVDeskServerError, tariff_group.delete)

        self.assertEqual(grace_period, 33)

    def test_expires_get_set(self):
        self.assertEquals(self.obj.get_expires_time() is None, True)

        self.obj.name = self.title
        self.obj.set_expires_time(1234567)
        self.assertEqual(self.obj.get_expires_time(), 1234567)

        self.obj.create()
        expires = self.obj.get_expires_time()
        self.obj.delete()

        self.assertEqual(expires, 1234567)

    def test_last_seen_time(self):
        self.assertEquals(self.obj.get_last_seen_time() is None, True)

    def test_last_seen_addr(self):
        self.assertEquals(self.obj.get_last_seen_addr() is None, True)

    def test_block_get_set(self):

        blocking = self.obj.get_block_time()
        self.assertEquals(isinstance(blocking, tuple), True)
        self.assertEquals(blocking[0] is None, True)
        self.assertEquals(blocking[1] is None, True)

        self.obj.name = self.title
        self.obj.set_block_time(1234567, 7654321)
        blocking = self.obj.get_block_time()
        self.assertEqual(blocking[0], 1234567)
        self.assertEqual(blocking[1], 7654321)

        self.obj.create()
        blocking = self.obj.get_block_time()
        self.obj.delete()
        self.assertEqual(blocking[0], 1234567)
        self.assertEqual(blocking[1], 7654321)

    def test_groups(self):
        self.assertEquals(self.obj.get_groups() >= 0, True)

        group_1 = pyavdesk.AVDeskGroup(AVDESK)
        group_1.name = 'Testing pyavdesk station group 1'
        group_1.create()
        group_1_id = group_1.get_id()
        group_2 = pyavdesk.AVDeskGroup(AVDESK)
        group_2.name = 'Testing pyavdesk station group 2'
        group_2.create()
        group_2_id = group_2.get_id()

        self.obj.name = self.title
        self.obj.add_to_groups([group_1, group_2.get_id()])
        self.obj.create()

        groups = self.obj.get_groups()
        self.obj.delete()

        group_1.delete()
        group_2.delete()

        self.assertEqual(len(groups), 2)
        self.assertIn(group_1_id, groups)
        self.assertIn(group_2_id, groups)


class AVDeskRightCheck(unittest.TestCase):

    def test_properties(self):
        everyone = pyavdesk.AVDeskGroup(AVDESK, pyavdesk.META_GROUP_IDS['EVERYONE'])
        rights = everyone.get_av_rights()
        self.assertEquals(isinstance(rights, list), True)
        self.assertEquals(isinstance(rights[0], dict), True)
        self.assertEquals(isinstance(rights[0]['code_text'], str), True)
        self.assertEquals(isinstance(rights[0]['code'], long), True)
        self.assertEquals(isinstance(rights[0]['status'], long), True)


class AVDeskAdministratorCheck(unittest.TestCase):

    def setUp(self):
        microtime = get_microtime()
        self.obj = pyavdesk.AVDeskAdmin(AVDESK)
        self.login = 'pyavdesk%s' % microtime.replace(' ', '').replace(':', '').replace('.', '').replace('-', '')
        self.title = 'Тестовый pyavdesk администратор (%s)' % microtime
        self.descr = 'This administrator is created by pyavdesk test script. If it is not removed automatically, that means that something went wrong.'
        self.descr_alt = 'This administrator is updated by pyavdesk test script. If it is not removed automatically, that means that something weird has happened.'

    def test_handle(self):
        self.assertEquals(self.obj._handle is None, False)

    def test_resource_name(self):
        self.assertEqual(self.obj._resource_name, 'admin')

    def test_connector(self):
        self.assertEqual(self.obj._connector, AVDESK)

    def test_id_get_set(self):
        self.assertEquals(self.obj.get_id() is None, True)
        self.obj.set_id('test_admin')
        self.assertEqual(self.obj.get_id(), 'test_admin')

    def test_name_get_set(self):
        self.assertEquals(self.obj.get_name() is None, True)
        self.obj.set_name('test_admin_name')
        self.assertEqual(self.obj.get_name(), 'test_admin_name')

    def test_last_name_get_set(self):
        self.assertEquals(self.obj.get_last_name() is None, True)
        self.obj.set_last_name('test_admin_last_name')
        self.assertEqual(self.obj.get_last_name(), 'test_admin_last_name')

    def test_last_name_get_set(self):
        self.assertEquals(self.obj.get_middle_name() is None, True)
        self.obj.set_middle_name('test_admin_middle_name')
        self.assertEqual(self.obj.get_middle_name(), 'test_admin_middle_name')

    def test_description_get_set(self):
        self.assertEquals(self.obj.get_description() is None, True)
        self.obj.set_description('test_admin_descr')
        self.assertEqual(self.obj.get_description(), 'test_admin_descr')

    def test_password_get_set(self):
        self.assertEquals(self.obj.get_password() is None, True)
        self.obj.set_password('test_admin_passwd')
        self.assertEqual(self.obj.get_password(), 'test_admin_passwd')

    def test_readonly_get_set(self):
        self.assertFalse(self.obj.get_readonly())
        self.obj.set_readonly(True)
        self.assertEqual(self.obj.get_readonly(), True)
        self.obj.set_readonly(False)
        self.assertEqual(self.obj.get_readonly(), False)

    def test_get_time_created_modified(self):
        self.assertEquals(self.obj.get_time_created() is None, True)
        self.assertEquals(self.obj.get_time_modified() is None, True)

        self.obj.name = self.title
        self.obj.login = self.login
        self.obj.description = self.descr
        self.obj.create()
        created = self.obj.get_time_created()
        modified = self.obj.get_time_modified()
        self.obj.delete()
        self.assertEquals(created is None, False)
        self.assertEquals(modified is None, False)

    def test_create_update_delete(self):
        self.obj.login = self.login
        self.obj.name = self.title
        self.obj.description = self.descr
        result = self.obj.create()

        self.assertEqual(result, True)
        self.assertEquals(self.obj.id is None, False)
        self.assertEqual(self.obj.name,  self.title)

        new_description = self.descr_alt
        self.obj.description = new_description
        result = self.obj.update()
        self.assertEqual(result, True)
        self.assertEqual(self.obj.description,  new_description)

        result = self.obj.delete()
        self.assertEqual(result, True)

    def test_save(self):
        self.obj.name = self.title
        self.obj.login = self.login
        self.obj.description = self.descr
        created = self.obj.save()
        self.assertTrue(created)
        self.assertEqual(self.obj.name, self.title)
        self.assertEqual(self.obj.description, self.descr)

        self.obj.description = self.descr_alt
        updated = self.obj.save()
        self.assertTrue(updated)
        self.assertEqual(self.obj.name, self.title)
        self.assertEqual(self.obj.description, self.descr_alt)

        deleted = self.obj.delete()
        self.assertTrue(deleted)

    def test_groups(self):
        self.assertEquals(self.obj.get_groups() >= 0, True)
        self.assertFalse(self.obj.type_is_global_admin())
        self.assertFalse(self.obj.type_is_group_admin())

        group_1 = pyavdesk.AVDeskGroup(AVDESK)
        group_1.name = 'Testing pyavdesk admin group 1'
        group_1.create()
        group_1_id = group_1.get_id()
        group_2 = pyavdesk.AVDeskGroup(AVDESK)
        group_2.name = 'Testing pyavdesk admin group 2'
        group_2.create()
        group_2_id = group_2.get_id()

        self.obj.name = self.title
        self.obj.login = self.login
        self.obj.add_to_groups([group_1, group_2.get_id()])
        self.obj.create()

        self.assertFalse(self.obj.type_is_global_admin())
        self.assertTrue(self.obj.type_is_group_admin())

        groups = self.obj.get_groups()

        self.obj.make_global_admin()
        self.obj.save()

        self.assertTrue(self.obj.type_is_global_admin())
        self.assertFalse(self.obj.type_is_group_admin())

        self.obj.delete()

        group_1.delete()
        group_2.delete()

        try:
            self.assertEqual(groups, [group_1_id, group_2_id])
        except AssertionError as e:
            # For AV-Desk 6.2 handling only one group per administrator.
            self.assertEqual(groups, [group_1_id,])


if __name__ == "__main__":
    unittest.main()
