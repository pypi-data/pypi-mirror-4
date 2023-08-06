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


import logging
from os import path
from ctypes.util import find_library

# Note that ctypes also imported in structures file.
from structures import *

MODULE_PATH = path.dirname(__file__)
# We try to use the latest libdwavdapi available in the system.
API_LIB = ctypes.CDLL(find_library('dwavdapi'), use_errno=True)
if API_LIB._name is None:
    API_LIB = None

# dwavdapi library version that is expected to work with this version of pyavdesk.
LIBRARY_EXPECTED_VERSION = '2.1'

# Base meta groups identifiers are given below.
META_GROUP_IDS = {
    'EVERYONE': '20e27d73-d21d-b211-a788-85419c46f0e6',
    'STATUS': '48afe720-953c-4075-856c-361f3ff06b6d',
    'TRANSPORT': '159e383d-f853-4bc5-9e18-c40144542aca',
    'PLATFORM': 'f991915f-8a15-4cf7-817a-d81d156d2bbe',
    'UNGROUPED': '411dac63-2a3e-4ce8-af4f-1fbeb94242ef',
    'TARIFFS': '994992e8-be71-4d31-a1f5-5b7786262611',
}

# Below are base tariff groups identifiers.
TARIFF_IDS = {
    'CLASSIC': '2888b7ff-3625-465e-bcb8-957de17f6458',
    'STANDART': 'ebe76ffc-69e1-4757-b2b3-41506832bc9b',
    'PREMIUM': '91644cc3-1dc1-42dc-a41e-5ea001f5538d',
    'PREMIUM_SRV': '01fe9e60-6570-11de-b827-0002a5d5c51b',
    # Trariffs introduced in AV-Desk 6.2.
    'FREE': '2c213cd2-eba1-4a0e-9f76-95e5e756d48c',
    'MOBILE': '4e87fd11-4a35-4ec1-bedd-29669b357e35',
    # Tariffs below contain server components.
    'SRV_CLASSIC': '673b0574-d11d-b211-9b4e-de33edc4ef1b',
    'SRV_STANDART': '800af701-d21d-b211-9b54-de33edc4ef1b',
    'SRV_PREMIUM': '382a6f16-d21d-b211-9b56-de33edc4ef1b',
}

# Components identifiers (see ``AVDeskGroup::set_av_component()``).
AV_COMPONENT_IDS = {
    'SCANNER_32W': 0x1,
    'SPIDERGUARD_9X': 0x2,
    'SPIDERGUARD_NT': 0x4,
    'SPIDERGUARD_NT_SERVER': 0x10,
    'SPIDERMAIL_HOME': 0x8,
    'SPIDERGATE': 0x20,
    'SELFPROTECTION': 0x40,
    'ANTISPAM_VADERETRO': 0x80,
    'OUTLOOK_PLUGIN': 0x100,
    'FIREWALL': 0x200
}

# Component state identifiers (see ``AVDeskGroup::set_av_component()``).
AV_COMPONENT_STATES = {
    'DISABLED': 0,
    'OPTIONAL': 1,
    'REQUIRED': 2
}

# AV-agent package platforms identifiers.
AV_PACKAGE_PLATFORMS = {
    'WINDOWS': 1,
    'ANDROID': 2,
    'MACOS': 3,
    'LINUX_32': 4,
    'LINUX_64': 5,
}

# History event types identifiers (see ``AVDeskStation::get_history()``).
HISTORY_EVENT_TYPES = {
    'STATION_EXPIRES_SET': 2,
    'STATION_BLOCK_SET': 3,
    'STATION_TARIFF_CHANGED': 4,
    'STATION_CREATED': 5,
    'STATION_DELETED': 6,
    'STATION_RESTORED': 7
}

# Uinitialized fields values constants used by dwavdapi.
VAR_UINITIALIZED_NUM = -200
VAR_UINITIALIZED_STR = None

def library_version_satisfied():
    """Tests whether version of dwavdapi library found in the system
    is the same as version pyavdesk was designed to work with.
    Returns a tuple where the first element is True if version is satisfied, otherwise False;
    and the second element is actual number of library currently installed.

    """
    if API_LIB is None:
        raise AVDeskError('dwavdapi library required for pyavdesk to function is not found in the system.')

    try:
        version = API_LIB.dwavdapi_version
        version.restype = ctypes.c_char_p
        version = version()
        if version.startswith(LIBRARY_EXPECTED_VERSION):
            return True, version
    except AttributeError:
        # Library is very very very old %)
        pass
    return False, None

def set_log_level(lvl):
    """This sets module logging to a desired level and turns on log pretty formatting.
    `lvl` Should be logging level from  `logging` module. E.g.: logging.DEBUG.

    """
    logging.basicConfig(level=lvl, format="** %(asctime)s - %(name)s - %(levelname)s\n%(message)s\n")


class AVDeskError(Exception):
    """This is a basic exception type used throughout the module."""

    def __init__(self, message, lib_function=None, lib_errno=None, lib_function_args=None):
        Exception.__init__(self, message)
        self.lib_function = lib_function
        self.lib_errno = lib_errno
        self.lib_function_args = lib_function_args


class AVDeskLibraryError(AVDeskError):
    """This is an exception type used to represent errors returned by dwavdapi library."""
    pass


class AVDeskServerError(AVDeskError):
    """This is an exception type used to represent errors returned by server."""
    pass


class _AVDeskLogger(object):
    """Logger class shared among AVDeskServer resources classes."""

    def __init__(self):
        self._logger = None

    def __get__(self, instance, owner):
        if self._logger is None:
            self._logger = logging.getLogger(owner.__module__ + '.' + owner.__name__)
        return self._logger


class _AVDeskResource(object):
    """Basic class for all classes describing AV-Desk resources.
    It also implements some helper methods.

    """

    # Logger instance for class.
    __logger = _AVDeskLogger()
    # Resource handle.
    _handle = None
    # Resource type identifier (name). Is used to build up `dwavdapi` function name.
    _resource_name = ''
    # Link to ctypes interface.
    _api = API_LIB
    # Handle to the AVDesk server resource.
    _connector = None
    # Name of callable to get resource identifier from.
    _id_callable = 'get_id'

    def get_resource_id(self):
        """Helper method to get resource identifier, which can be passed to such resource
        manipulation methods as ``get_info()`` and ``delete()``.

        :return: resource identifier as string

        """
        return getattr(self, self._id_callable)()

    def _init_handle(self, handle=None):
        """Initializes a resource handle."""
        if handle is None:
            # 64bit systems urge for function result type casting.
            self._handle = ctypes.c_void_p(self._lib_call(self._api_func_name('init'), restype=ctypes.c_void_p))
        else:
            self._handle = handle

    def _reinit_handle(self):
        """This should be used to free stucture memory when reusing the same handle
        in subsequent structure modifying library calls.
        """
        self._handle = ctypes.c_void_p()
        self._lib_call(self._api_func_name('reinit'), (ctypes.byref(self._handle),))

    def _destroy_handle(self):
        """Destroys resource handle if any."""
        if self._handle:
            self._lib_call(self._api_func_name('destroy'), (self._handle,))

    def _api_func_name(self, postfix):
        """Returns `dwavdapi` function name built up from resource name, etc."""
        prefix = 'dwavdapi_'
        if postfix.find(prefix) > -1:
            return postfix
        return ('%s%s_%s' % (prefix, self._resource_name, postfix)).replace('__', '_')

    def _lib_call(self, func_name, args_list=None, restype=None):
        """Performs `dwavdapi` function call through ctypes interface."""
        if args_list is None:
            args_list = []
        attr = getattr(self._api, func_name)
        if restype is not None:
            attr.restype = restype
        self.__logger.debug('"%s" called with  %s.' % (func_name, args_list))
        result = attr(*args_list)
        self.__logger.debug('"%s" result: %s' % (func_name, result))
        return result

    def _get_string_at_pointer(self, pointer):
        """Helper ctypes method that fetches string at pointer."""
        return ctypes.string_at(pointer)

    def _test_library_version(self):
        satisfied = library_version_satisfied()
        if not satisfied[0]:
            self.__logger.warning('Unexpected dwavdapi library version found in the system. Required: %s. Found: %s.' % (LIBRARY_EXPECTED_VERSION, satisfied[1]))

    def _get_string_param(self, param_name):
        """Performs `dwavdapi` function call returning result as a string."""
        return self._lib_call(self._api_func_name(param_name), (self._get_handle(),), restype=ctypes.c_char_p)

    def _api_call(self, func_name, args, restype=None):
        """Performs `dwavdapi` function call with result checked on error.
        Throws AVDeskError exception on error.
        
        """
        func_name = self._api_func_name(func_name)
        result = self._lib_call(func_name, args, restype=restype)
        # 1 is a function call failure constant DWAVDAPI_FAILURE used in the library.
        if result==1:
            error_num = ctypes.get_errno()
            if error_num==2029:  # Server error constant from the library.
                error_num = self._api.dwavdapi_srv_errno(self._connector._get_handle())
                error_descr = ctypes.c_char_p()
                self._api.dwavdapi_srv_error(self._connector._get_handle(), ctypes.byref(error_descr))
                raise AVDeskServerError(error_descr.value, func_name, error_num, lib_function_args=args)
            else:
                error_descr = ctypes.c_char_p()
                self._api.dwavdapi_strerror(ctypes.byref(error_descr), error_num)
                raise AVDeskLibraryError(error_descr.value, func_name, error_num, lib_function_args=args)
        return result

    def _get_handle(self):
        """Returns handle of a current resource."""
        return self._handle

    def _get_structure(self, struct_class, func_name, args_list=None):
        """Performs `dwavdapi` function call returning structure at pointer
        containing in function's argument as a dictionary.

        """
        if args_list is None:
            args_list = []
        info_ptr = ctypes.POINTER(struct_class)()
        func_args = [self._connector._get_handle(), ctypes.byref(info_ptr)] + args_list
        self._api_call(func_name, func_args)
        try:
            return info_ptr.contents.as_dict()
        except ValueError:
            return {}

    def _get_structure_from_result(self, struct_class, func_name, args_list=None, result_is_ptr=False):
        """Performs `dwavdapi` function call returning resulting structure as a dictionary."""
        if args_list is None:
            args_list = []
        restype = struct_class
        if result_is_ptr:
            restype = ctypes.c_void_p
        result = self._api_call(func_name, args_list, restype=restype)
        if result is None:
            return {}
        if result_is_ptr:
            # Function call returned pointer, we need to cast it into structure.
            result = ctypes.cast(result, ctypes.POINTER(struct_class))
            result = result.contents.as_dict()
        return result

    def _get_list_from_remote(self, resource):
        """Performs a number of `dwavdapi` function calls to form and return from a remote
        a list of objects of type which ID is given in `resource` parameter."""
        resource_class = 'AVDesk%s' % resource.capitalize()
        list_handle = ctypes.c_void_p()
        self._lib_call('dwavdapi_%s_get_list' % resource,(self._get_handle(), ctypes.byref(list_handle)))

        items = []
        if list_handle.value is not None:
            while True:
                item_current_ptr = ctypes.c_void_p(self._api_call('dwavdapi_list_current_data', (list_handle,), restype=ctypes.c_void_p))

                item_current = ctypes.c_void_p()
                self._api_call('dwavdapi_%s_ctor' % resource, (ctypes.byref(item_current), item_current_ptr))

                items.append(globals()[resource_class](self, predefined_handle=item_current))
                if self._lib_call('dwavdapi_list_next', (list_handle,)):
                    break
            self._lib_call('dwavdapi_list_destroy', (list_handle, None))

        return items

    def _structures_list(self, struct_cls, resource=None, handle=None, item_processor=None, args_list=[], struc_handle_to_dict=False):
        """Returns a list of dictionaries with structures data from structures
        connected through `next` field.

        """
        if resource is None:
            resource = '%ss' % struct_cls.__name__.lstrip('Struct').lower()

        if handle is None:
            handle = self._get_handle()
            
        structs = []
        if 'get' in resource:
            list_handle = ctypes.c_void_p()
            args = [handle, ctypes.byref(list_handle)] + args_list
            self._lib_call(self._api_func_name('%s_list' % resource), args)
        else:
            list_handle = ctypes.c_void_p(self._lib_call(self._api_func_name('%s_list' % resource), (handle,), restype=ctypes.c_void_p))

        if list_handle is None or (hasattr(list_handle, 'value') and list_handle.value is None):
            return structs

        while True:
            item_current_ptr = ctypes.c_void_p(self._api_call('dwavdapi_list_current_data', (list_handle,), restype=ctypes.c_void_p))
            result = ctypes.cast(item_current_ptr, ctypes.POINTER(struct_cls))
            data = result.contents.as_dict()
            if item_processor is not None:
                data = item_processor(item_current_ptr, data)
            if struc_handle_to_dict:
                data['_struc_h'] = item_current_ptr
            structs.append(data)
            if self._lib_call('dwavdapi_list_next', (list_handle,)):
                break

        return structs

    def _get_infected_objects_list(self, handle, data):
        """This is an item process function for infected object structure."""
        data['objects_list'] = self._structures_list(StructInfectionObject, 'dwavdapi_virus_infected_objects', handle=handle, struc_handle_to_dict=True)
        for obj in data['objects_list']:
            obj['originator_text'] = self._lib_call('dwavdapi_application_name', (obj['originator'],), restype=ctypes.c_char_p)
            obj['cure_status_id'] = self._lib_call('dwavdapi_infected_object_cure_status', (obj['_struc_h'],), restype=ctypes.c_uint)
            obj['cure_status_text'] = self._lib_call('dwavdapi_infected_object_cure_status_str', (obj['_struc_h'],), restype=ctypes.c_char_p)
            obj['object_type_text'] = self._lib_call('dwavdapi_infected_object_type_str', (obj['_struc_h'],), restype=ctypes.c_char_p)
            obj['infection_type_text'] = self._lib_call('dwavdapi_infection_type_str', (obj['_struc_h'],), restype=ctypes.c_char_p)
            del(obj['_struc_h'])
            del(obj['station_uuid'])
            del(obj['treatment'])
        return data

    def _get_list_from_array(self, array_length, func_name, func_args_list=None):
        """Returns Python list from C array returned by library function."""
        if func_args_list is None:
            func_args_list = []
        if not array_length:
            return []
        Array = ctypes.c_char_p * array_length
        array = self._lib_call(func_name, func_args_list, restype=ctypes.POINTER(Array))
        return [item for item in array.contents]

    def _get_list_from_array_simple(self, func_basename):
        """Returns Python list from C array using call to element count function,
        with further call to array retrival function.

        """
        items_count =  self._lib_call(self._api_func_name('%s_count' % func_basename), (self._get_handle(),))
        return self._get_list_from_array(items_count, self._api_func_name('%s_array' % func_basename), (self._get_handle(),))

    def __del__(self):
        """Destroys resource handle and frees memory."""
        self._destroy_handle()


class _AVDeskCommon(_AVDeskResource):
    """Class implements methods common to all AVDesk resources."""

    # Logger instance for class.
    __logger = _AVDeskLogger()
    # Boolean flag identifying that the resource already exists, used by save().
    _resource_exists = False

    def set_id(self, id):
        self._api_call('set_id', (self._get_handle(), id))

    def get_id(self):
        return self._get_string_param('id')

    def set_name(self, name):
        self._api_call('set_name', (self._get_handle(), name))

    def get_name(self):
        return self._get_string_param('name')

    def set_description(self, text):
        self._api_call('set_description', (self._get_handle(), text))

    def get_description(self):
        return self._get_string_param('description')

    def get_time_created(self):
        ts = self._api_call('created_time', (self._get_handle(),), restype=time_t)
        if ts == VAR_UINITIALIZED_NUM:
            return None
        return ts

    def get_time_modified(self):
        ts = self._api_call('modified_time', (self._get_handle(),), restype=time_t)
        if ts == VAR_UINITIALIZED_NUM:
            return None
        return ts

    id = property(get_id, set_id)
    name = property(get_name, set_name)
    description = property(get_description, set_description)
    time_created = property(get_time_created)
    time_modified = property(get_time_modified)

    def __init__(self, connector_resource, resource_id=None, predefined_handle=None):
        """Initializes AVDesk resource.

        :param connector_resource: should be AVDeskServer resource handle.
        :param resource_id: if set server call is performed to get information for resource with given ID.
        :param predefined_handle: if set, resource data could be fetched from a resource at given handle.
        :raises: :class:`AVDeskError` on failure

        """
        self._test_library_version()
        self._init_handle(predefined_handle)
        self._connector = connector_resource
        if resource_id is not None:
            self.retrieve_info(resource_id)

    def retrieve_info(self, resource_id=None):
        """Performs a server call to retrieve complete resource information by its ID and
        puts it into object's properties.

        :param resource_id: specific ID of the resource. If *None*, ID is taken from the object itself.
        :raises: :class:`AVDeskError` on failure

        Example::

            # resource_obj contains no additional info.
            assert resource_obj.name is None

            # After the following request
            resource_obj.retrieve_info('some_resource_id')
            
            # resource_obj contains additional info.
            assert resource_obj.name is not None

        """
        if resource_id is None:
            resource_id = self.get_resource_id()
        self._handle = ctypes.c_void_p()
        self._api_call('get_info', (self._connector._get_handle(), ctypes.byref(self._handle), resource_id))
        self._resource_exists = True

    def save(self, auto_retrieve=True):
        """A convinience method that automatically creates new resource on server if it doesn't
        exists or updates it if it does.

        Under the hood it switches between ``create()`` and ``update()`` methods.

        :param auto_retrieve: boolean to specify whether an additional call
            to server is required after the `save` operation to retrieve
            full resource data. Default: True.
        :return: *True* on success
        :raises: :class:`AVDeskError` on failure

        .. warning::
            Setting ``auto_retrieve`` to False may increase operation performance, but also
            may leave the resource object data in a not up-to-date state. It is advised
            that ``auto_retrieve`` set to False is only used when the resource object
            won't be used further after the operation.

        Example::

            saved = resource_obj.save()

        """
        if self._resource_exists:
            return self.update(auto_retrieve=auto_retrieve)
        else:
            return self.create(auto_retrieve=auto_retrieve)

    def create(self, auto_retrieve=True):
        """Performs a server call to create resource with properties defined in object.

        .. note::
            There is a convinience method :func:`save()` to handle both ``create`` and ``update`` operations.

        :param auto_retrieve: boolean to specify whether an additional call
            to server is required after the `create` operation to retrieve
            full resource data. Default: True.
        :return: *True* on success
        :raises: :class:`AVDeskError` on failure

        .. warning::
            Setting ``auto_retrieve`` to False may increase operation performance, but also
            may leave the resource object data in a not up-to-date state. It is advised
            that ``auto_retrieve`` set to False is only used when the resource object
            won't be used further after the operation.

        Example::

            created = resource_obj.create()

        """
        resource_id = ctypes.c_char_p()
        self._api_call('add', (self._connector._get_handle(), self._get_handle(), ctypes.byref(resource_id)))
        resource_id = self._get_string_at_pointer(resource_id)
        if auto_retrieve:
            self.retrieve_info(resource_id)
        self._resource_exists = True
        return True

    def update(self, auto_retrieve=True):
        """Performs server call in attempt to update the resource with information
        from class properties.

        .. note::
            There is a convinience method :func:`save()` to handle both ``create`` and ``update`` operations.

        :param auto_retrieve: boolean to specify whether an additional call
            to server is required after the `update` operation to retrieve
            full resource data. Default: True.
        :return: *True* on success
        :raises: :class:`AVDeskError` on failure

        .. warning::
            Setting ``auto_retrieve`` to False may increase operation performance, but also
            may leave the resource object data in a not up-to-date state. It is advised
            that ``auto_retrieve`` set to False is only used when the resource object
            won't be used further after the operation.

        Example::

            updated = resource_obj.update()

        """
        self._api_call('change', (self._connector._get_handle(), self._get_handle()))
        if auto_retrieve:
            self.retrieve_info()
        self._resource_exists = True
        return True

    def delete(self, **kwargs):
        """Performs server call in an attempt to delete the resource.

        :return: *True* on success
        :raises: :class:`AVDeskError` on failure

        Example::

            deleted = resource_obj.delete()

        """
        self._api_call('delete', (self._connector._get_handle(), self.get_resource_id()))
        self._resource_exists = False
        return True


class _AVDeskShared(_AVDeskResource):
    """Introduces methods shared among several AVDesk resources."""

    def get_key(self):
        """Performs a server call to retrieve a dictionary with key information for the resource.

        :return: dictionary with key information
        :raises: :class:`AVDeskError` on failure

        Example::

            key = resource_obj.get_key()

        An example of returned dictionary::

            {
                'inherited_group_id': '20e27d73-d21d-b211-a788-85419c46f0e6',
                'key': '=?ASCII?B?OyBEcldlYjMyIHY0LjE2?=' # This is a key in Base64 format.
            }

        """
        key = self._get_structure_from_result(StructKey, 'key', [self._get_handle()], result_is_ptr=True)
        if key=={}:
            return None
        return key

    def set_parent(self, id_or_obj):
        """Sets parent resource for the current resource.

        :param id_or_obj: Parent resource object or ID.
        :raises: :class:`AVDeskError` on failure

        Example::

            child_resource_obj.set_parent(parent_resource_obj)
            # Is equivalent to:
            child_resource_obj.set_parent('parent_resource_id')

        """
        if isinstance(id_or_obj, _AVDeskResource):
            id_or_obj = id_or_obj.get_resource_id()
        self._api_call('set_parent_id', (self._get_handle(), id_or_obj))

    def get_parent(self, as_id=True):
        """Performs a server call to retrieve a parent resource for the current resource.

        :param as_id: boolean. If *True* resource object is returned, if *False* - resources' ID
        :return: object or ID. See ``as_id`` parameter.
        :raises: :class:`AVDeskError` on failure

        Example::

            parent = resource_obj.get_parent()
            print 'Parent ID - %s' % parent

        """
        parent = self._api_call('parent_id', (self._get_handle(),), restype=ctypes.c_char_p)
        if parent is None:
            return None
        if as_id:
            return parent
        parent = self.__class__(self._connector, parent)
        return parent

    #: This *property* is used to get or det parent resource for the current resource.
    parent = property(get_parent, set_parent)
    #: This *property* is used to get key information for the current resource.
    key = property(get_key)

    def send_message(self, message_text, url='', url_text='', logo_abs_path='', logo_text='', logo_url=''):
        """Sends a message to all group participants.

        :param message_text: Message text which can contain {link} macros to place link given in link parameters to
        :param url: URL to be placed in {link} macros
        :param url_text: URL description text to be placed in {link} macros
        :param logo_abs_path: Absolute path to a logo .bmp file to show in message
        :param logo_text: Description text for a logo
        :param logo_url: URL to go to on a logo click
        :return: *True* on success
        :raises: :class:`AVDeskError` on failure

        Example::

            group.send_message('Hello from pyavdesk!')
        
        """
        if self.get_resource_id() is None:
            return False
        else:
            message = StructMessage(message=message_text, url=url, url_text=url_text, logo=logo_abs_path, logo_text=logo_text, logo_url=logo_url)
            self._api_call('send_message', (self._connector._get_handle(), self.get_resource_id(), ctypes.byref(message)))
        return True

    def get_emails(self):
        """Returns a list of e-mails defined for the resource.

        :return: list of e-mails

        Example::

            emails = resource_obj.get_emails()

        """
        return self._get_list_from_array_simple('emails')

    def add_emails(self, emails_list):
        """Adds given emails to a list of e-mails defined for the resource.

        .. note::
            This method does not send data to server, for this to be done one needs to save resource object.

        :param emails_list: list of e-mails

        Example::

            resource_obj.add_emails(['person1@server.com', 'person2@server.com'])

        """
        for email in emails_list:
            self._api_call('add_email', (self._get_handle(), email))

    def delete_emails(self, emails_list):
        """Removes given emails from a list of e-mails defined for the resource.

        .. note::
            This method does not send data to server, for this to be done one needs to save resource object.

        :param emails_list: list of e-mails

        Example::

            resource_obj.delete_emails(['person1@server.com', 'person2@server.com', 'person3@server.com'])

        """
        for email in emails_list:
            self._api_call('delete_email', (self._get_handle(), email))

    def _av_item_extend(self, structs_list, statuses, code_interpreter):
        """Helper method extending component or right information dictionary."""
        new_structs = []
        for struct in structs_list:
            struct['code_text'] = self._api_call(code_interpreter, (struct['code'],), restype=ctypes.c_char_p)
            if 'status' in struct:
                try:
                    struct['status_text'] = statuses[struct['status']]
                except IndexError:
                    struct['status_text'] = None
            new_structs.append(struct)
        return new_structs

    def get_av_components(self):
        """Performs a server call to retrieve a list of antivirus application components information for the resource.

        :return: list of dictionaries with components data
        :raises: :class:`AVDeskError` on failure

        Example::

            components = resource_obj.get_av_components()

        An extract from returned list::

            [
                {
                    'status': 1,
                    'code': 105,
                    'parent_group_id': '2888b7ff-3625-465e-bcb8-957de17f6458',
                    'code_text': 'Dr.Web Firewall',
                    'status_text': 'Optional',
                    ...
                },
                ...
            ]

        """
        return self._av_item_extend(self._structures_list(StructComponent), ['Disabled', 'Optional', 'Required'], 'dwavdapi_application_name')

    def get_av_rights(self):
        """Performs a server call to retrieve a list of rights defined for the resource.

        :return: list of dictionaries with rigths data
        :raises: :class:`AVDeskError` on failure

        Example::

            rights = resource_obj.get_av_rights()

        An extract from returned list::

            [
                {
                    'status': 1,
                    'code': 53,
                    'parent_group_id': '2888b7ff-3625-465e-bcb8-957de17f6458',
                    'code_text': 'Uninstall Dr.Web Agent',
                    'status_text': 'Enabled',
                    ...
                },
                ...
            ]

        """
        return self._av_item_extend(self._structures_list(StructRight), ['Disabled', 'Enabled'], 'dwavdapi_right_name_by_code')


class _AVDeskGroupable(_AVDeskResource):
    """Introduces methods used by some AVDesk resources allowing
    placement in groups.
    
    """

    def add_to_groups(self, groups_list):
        """Add groups to resource association by group IDs or objects.

        :param groups_list: list of :class:`AVDeskGroup` instances, or a list of strings representing groups IDs
        :raises: :class:`AVDeskError` on failure

        .. note::
            Resource to group association is not sent to server until object's :func:`save()` is not called.

        .. warning::
            Some AV-Desk server versions (namely 6.2) might handle only one group per administrator.
            In that case only the first group from the given list is linked with
            the administrator.

        Example::

            resource_obj.add_to_groups(['my_group_id', my_another_group_obj])
            resource_obj.save()

        """
        for group_id in groups_list:
            if isinstance(group_id, AVDeskGroup):
                group_id = group_id.get_resource_id()

            self._api_call('add_to_group', (self._get_handle(), group_id))

    def delete_from_groups(self, groups_list):
        """Removes groups to resource association by group IDs or objects.

        :param groups_list: list of :class:`AVDeskGroup` instances, or a list of strings representing groups IDs
        :raises: :class:`AVDeskError` on failure

        .. note::
            Resource to group association is not sent to server until object's :func:`save()` is not called.

        Example::

            resource_obj.delete_from_groups(['my_group_id', my_another_group_obj])
            resource_obj.save()

        """
        for group_id in groups_list:
            if isinstance(group_id, AVDeskGroup):
                group_id = group_id.get_resource_id()
            self._api_call('delete_from_group', (self._get_handle(), group_id))

    def get_groups(self, as_id=True):
        """Performs a server call and returns a list of groups associated with the resource.

        :param as_id: boolean. If *True* list of :class:`AVDeskGroup` instances is returned,
            if *False* - list of strings representing groups IDs
        :return: list of objects which type is defined by `as_id` parameter
        :raises: :class:`AVDeskError` on failure

        .. note::
            Objects in the list returned have only basic information. To get full infomation
            use :func:`AVDeskGroup.retrieve_info()`.

        Example::

            groups = resource_obj.get_groups()
            for group in groups:
                print 'Group ID - %s' % group.id

        """
        groups_ids = self._get_list_from_array_simple('groups')
        if as_id:
            return groups_ids
        obj_list = []
        for child_id in groups_ids:
            obj_list.append(AVDeskGroup(self._connector, child_id))
        return obj_list


class AVDeskServer(_AVDeskResource):
    """This is a basic pyavdesk class, providing server connection handle,
    and essential methods to manipulate server resources.

    .. note::

        If ``url`` parameter value contains `https` dwavdapi library will try to verify connection
        certificate automatically. This behavior can be changed with ``verify_connection_certificate()``.

    :param login: is the login of user from whose name module issues connection
    :param password: user password used for connection
    :param url: should be set to AV-Desk web-server URL
    :param port: should be set to AV-Desk web-server port
    :param connection_timeout: connection timeout in seconds
    :return: :class:`AVDeskServer` instance
    :raises: :class:`AVDeskError` on failure

    Example::

        # Setting up the connection data with timeout equal to 5 seconds.
        av_server = pyavdesk.AVDeskServer('admin', 'password', 'http://192.168.1.70', connection_timeout=5)

    """

    _resource_name = 'srv'

    def __init__(self, login, password, url='http://127.0.0.1', port=9080, connection_timeout=2):
        """Creates server connection handle storing connection settings.

        .. note::

            If ``url`` parameter value contains `https` dwavdapi library will try to verify connection
            certificate automatically. This behavior can be changed with ``verify_connection_certificate()``.

        :param login: is the login of user from whose name module issues connection
        :param password: user password used for connection
        :param url: should be set to AV-Desk web-server URL
        :param port: should be set to AV-Desk web-server port
        :param connection_timeout: connection timeout in seconds
        :return: :class:`AVDeskServer` instance
        :raises: :class:`AVDeskError` on failure

        """
        self._test_library_version()
        # 64bit systems urge for function result type casting.
        self._handle = ctypes.c_void_p(self._lib_call('dwavdapi_init', restype=ctypes.c_void_p))
        self._connector = self
        self._api_call('dwavdapi_set_connect_info', (self._handle, url, port, login, password))
        # 2 seconds if the default value in dwavdapi library.
        if connection_timeout != 2 and connection_timeout >=0:
            self._lib_call('dwavdapi_set_connect_timeout', (self._handle, connection_timeout))

    def run_task(self, task_id):
        """Requests a server to execute the task defined by its ID string.

        :param task_id: task identifier string.
        :raises: :class:`AVDeskError` on failure

        """
        return not bool(self._api_call('run_task', (self._handle, task_id)))

    def verify_connection_certificate(self, do_verify, certificate_path=None):
        """Gives *dwavdapi* library an instruction to verify or not to verify connection certificate.

        :param do_verify: boolean. If *True* connection certificate will be verified.
        :param certificate_path: expects full path to root certificate to verify connection validity against, or *None*
            is system certificates should be used.
        :raises: :class:`AVDeskError` on failure

        """
        self._lib_call('dwavdapi_set_connect_ssl_verify', (self._handle, int(do_verify)))
        self._api_call('dwavdapi_set_connect_ssl_crt', (self._handle, certificate_path))

    def get_info(self):
        """Makes request to a server and returns a dictionary with basic information about server.

        Example::

            info = av_server.get_info()

        An extract from dictionary returned::

            {
                'api_build': '201110201',
                'groups_system': 85,
                'uptime': 98544,
                'tariffs_total': 25,
                'stations_total': 283,
                'os': 'Linux',
                 ...
            }

        :return: dictionary
        :raises: :class:`AVDeskError` on failure

        """
        return self._get_structure(StructServer, 'get_info')

    def set_user_agent(self, title):
        """Instructs *dwavdapi* library to use the given User Agent string on server requests.

        :param title: User Agent string.
        :return: boolean. *True* on success, overwise - *False*
        :raises: :class:`AVDeskError` on failure

        """
        return not bool(self._api_call('dwavdapi_set_user_agent', (self._handle, title)))

    def get_key_info(self):
        """Makes request to a server and returns a dictionary with information about AV-Desk server key.

        Example::

            info = av_server.get_key_info()

        An extract from dictionary returned::

            {
                'expires_ts': 1341867133,
                'created_ts': 1310158333,
                'servers': 1,
                'sn': None,
                'md5': '6036761418df7065dab1518afd2cf1e7'
                ...
            }

        :return: dictionary
        :raises: :class:`AVDeskError` on failure

        """
        return self._get_structure(StructServerKey, 'get_key_info')

    def get_statistics(self, ts_from=0, ts_till=0, virus_limit=10):
        """Makes request to a server and returns a dictionary with overall server statistics.

        :param ts_from: timestamp of when statistics starts. If 0 - statistics starts at year 1970. Default 0.
        :param ts_till: timestamp of when staristics ends. If 0 - statistics ends today. Default 0.
        :param virus_limit: virus statistics limiter, to return no more than a given number of viruses. Default 10.
        :return: dictionary
        :raises: :class:`AVDeskError` on failure

        Example::

            stats = av_server.get_statistics()

        An extract from dictionary returned::

            {
                'groups_system': 85,
                'tariffs_total': 25,
                'traffic': {
                    'total': 1140022.0,
                    'out': 322671.0,
                    'in': 817351.0
                },
                'stations_total': 283,
                'stations_state': {
                    'unactivated': 270,
                    'activated': 13,
                    'deinstalled': 0,
                    ...
                },
                ...
            }

        """
        statistics_struc_ptr = ctypes.c_void_p()
        self._api_call('get_statistics', (self._handle, ctypes.byref(statistics_struc_ptr), time_t(ts_from), time_t(ts_till), virus_limit))
        statistics = {
            'traffic': self._get_structure_from_result(StructServerTraffic, 'statistics_traffic', [statistics_struc_ptr]).as_dict(),
            'stations_state': self._get_structure_from_result(StructStationsState, 'statistics_stations_state', [statistics_struc_ptr]).as_dict(),
            'stations_total': self._lib_call('dwavdapi_srv_statistics_stations_total', (statistics_struc_ptr,), ctypes.c_ulong),
            'groups_total': self._lib_call('dwavdapi_srv_statistics_groups_total', (statistics_struc_ptr,), ctypes.c_ulong),
            'groups_custom': self._lib_call('dwavdapi_srv_statistics_groups_custom', (statistics_struc_ptr,), ctypes.c_ulong),
            'groups_system': self._lib_call('dwavdapi_srv_statistics_groups_system', (statistics_struc_ptr,), ctypes.c_ulong),
            'tariffs_total': self._lib_call('dwavdapi_srv_statistics_tariffs_total', (statistics_struc_ptr,), ctypes.c_ulong),
            'infections': self._get_structure_from_result(StructInfection, 'statistics_infections', [statistics_struc_ptr]).as_dict(),
            'scans': self._get_structure_from_result(StructScan, 'statistics_scans', [statistics_struc_ptr]).as_dict(),
            'viruses': self._structures_list(StructVirus, 'statistics_viruses', handle=statistics_struc_ptr, item_processor=self._get_infected_objects_list),
        }
        self._api_call('statistics_destroy', (statistics_struc_ptr,))

        return statistics

    def switch_to_debug_mode(self, log_filepath=None):
        """Permanently switches dwavdapi library into debug mode when debugging information including
        server responses is written into a file.

        :param log_filepath: absolute path to file to write logs into. If *None* `libdwavdapi.log` in module's
            directory will be used.
        :return: boolean. *True* if successfully switched, overwise - *False*
        :raises: :class:`AVDeskError` on failure

        """
        if log_filepath is None:
            log_filepath = path.join(MODULE_PATH, 'pyavdesk.log')
        return not bool(self._lib_call('dwavdapi_debug_init', (log_filepath,)))

    def new_group(self, group_name, id=None, parent_group=None):
        """Initializes new :class:`AVDeskGroup` object with given parameters
        and returns it for further usage.

        :param group_name: name for the group
        :param id: group ID. If *None* group ID is generated by server and available from ``AVDeskGroup.id``
            after object is saved
        :param parent_group: parent group ID or object. Note: parent group must already exist on server.
        :return: :class:`AVDeskGroup`

        Example::

            group = avdesk.new_group('My Group', parent_group=my_parent_group)
            group.save()
            print 'Server generated group ID - "%s"' % group.id

        """
        group = AVDeskGroup(self)
        group.set_name(group_name)
        if id is not None:
            group.set_id(id)
        if parent_group is not None:
            group.set_parent(parent_group)
        return group

    def get_group(self, group_id):
        """Returns group resource object from server by ID.

        :param group_id: group ID to retrieve information for
        :return: :class:`AVDeskGroup` instance
        :raises: :class:`AVDeskError` on failure

        Example::

            everyone = av_server.get_group(pyavdesk.META_GROUP_IDS['EVERYONE'])

        In this example we use **META_GROUP_IDS** dictionary defined in the module
        to get 'EVERYONE' meta-group ID from to pass it to the method.

        """
        return AVDeskGroup(self, group_id)

    def new_administrator(self, administrator_login, password=None):
        """Initializes new :class:`AVDeskAdmin` object with given parameters
        and returns it for further usage.

        :param administrator_login: login for new administrator
        :param password: password for new administrator. If *None* password is generated by server and available
            from ``AVDeskAdmin.password`` after object is saved.
        :return: :class:`AVDeskAdmin`

        Example::

            administrator = avdesk.new_administrator('fred_colon')
            administrator.save()
            print 'Server generated password - "%s"' % administrator.password

        """
        admin = AVDeskAdmin(self)
        admin.set_login(administrator_login)
        if password is not None:
            admin.set_password(password)
        return admin

    def get_administrator(self, administrator_login):
        """Returns administrator resource object from server by login.

        :param administrator_login: administrator login to retrieve information for
        :return: :class:`AVDeskAdmin` instance
        :raises: :class:`AVDeskError` on failure

        Example::

            admin_fred = av_server.get_administrator('fred_colon')
            print 'Admin ID - %s' % admin_fred.id

        """
        return AVDeskAdmin(self, administrator_login)

    def new_tariff(self, tariff_name, id=None, parent_tariff=None, grace_period=None):
        """Initializes new :class:`AVDeskTariff` object with given parameters
        and returns it for further usage.

        :param tariff_name: name for the tariff group
        :param id: tariff group ID. If *None* tariff group ID is generated by server and available
            from ``AVDeskTariff.id`` after object is saved.
        :param parent_tariff: parent tariff group ID or object. Note: parent tariff group must already exist on server.
        :param grace_period: grace period rot this tariff in *days*.
        :return: :class:`AVDeskTariff`

        Example::

            tariff = avdesk.new_tariff('My Tariff', parent_tariff='my_parent_tariff_id')
            tariff.save()
            print 'Server generated tariff ID - "%s"' % tariff.id

        """
        tariff = AVDeskTariff(self)
        tariff.set_name(tariff_name)
        if id is not None:
            tariff.set_id(id)
        if grace_period is not None:
            tariff.grace_period = grace_period
        if parent_tariff is not None:
            tariff.set_parent(parent_tariff)
        return tariff

    def get_tariff(self, tariff_id):
        """Returns tariff group resource object from server by ID.

        :param tariff_id: tariff group ID to retrieve information for
        :return: :class:`AVDeskTariff` instance
        :raises: :class:`AVDeskError` on failure

        Example::

            tariff_group = avdesk.get_tariff('my_tariff')
            print tariff_group.name

        """
        return AVDeskTariff(self, tariff_id)

    def new_station(self, id=None, parent_group=None, tariff=None):
        """Initializes new :class:`AVDeskStation` object with given parameters
        and returns it for further usage.

        :param id: station ID. If *None* station ID is generated by server and available from ``AVDeskStation.id``
            after object is saved.
        :param parent_group: parent group ID or object. Note: parent group must already exist on server.
        :param tariff: tariff group ID or object. Note: tariff group must already exist on server.
        :return: :class:`AVDeskStation`

        Example::

            station = avdesk.new_station('My Station', parent_group=my_parent_group, tariff='tariff_id')
            station.save()
            print 'Server generated station ID - "%s"' % station.id

        """
        station = AVDeskStation(self)
        if id is not None:
            station.set_id(id)
        if parent_group is not None:
            station.set_parent(parent_group)
        if tariff is not None:
            station.set_tariff(tariff)
        return station

    def get_station(self, station_id):
        """Returns station resource object from server by ID.

        :param station_id: station ID to retrieve information for
        :return: :class:`AVDeskStation` instance
        :raises: :class:`AVDeskError` on failure

        Example::

            station = avdesk.get_station('my_station')
            print station.name

        """
        return AVDeskStation(self, station_id)

    def get_groups(self):
        """Returns a list of groups objects registered at server, performing server call.

        .. note::
            Objects in the list returned have only basic information. To get full infomation
            use :func:`AVDeskGroup.retrieve_info()`.

        :return: list of :class:`AVDeskGroup` instances
        :raises: :class:`AVDeskError` on failure

        Example::

            groups = av_server.get_groups()
            for group in groups:
                print 'A group with ID - %s' % group.id
        
        """
        return self._get_list_from_remote('group')

    def get_tariffs(self):
        """Returns a list of tariff group objects registered at server, performing server call.

        .. note::
            Objects in the list returned have only basic information. To get full infomation
            use :func:`AVDeskTariff.retrieve_info()`.

        :return: list of :class:`AVDeskTariff` instances
        :raises: :class:`AVDeskError` on failure

        Example::

            tariffs = av_server.get_tariffs()
            for tariff in tariffs:
                print 'Tariff named "%s"' % tariff.name

        """
        return self._get_list_from_remote('tariff')

    def get_stations(self, as_id=True):
        """Shortcut method that returns a list of stations registered at server
        through `Everyone` system group quering.

        :param as_id: boolean flag. If *True* list of :class:`AVDeskStation` instances is returned,
            if *False* - list of strings representing station IDs.
        :return: list of objects which type is defined by `as_id` parameter
        :raises: :class:`AVDeskError` on failure

        .. warning::
            Setting **as_id** parameter to *False* may lead to considerable server load, since separate server
            call is performed to retrieve full station information.
            One should bear it in mind when querying servers with large amount of stations.

        Example::

            stations = av_server.get_stations()
            for station in stations:
                print 'Station ID - %s' % station.id


        """
        return self.get_group(META_GROUP_IDS['EVERYONE']).get_stations(as_id)

    def get_administrators(self):
        """Returns a list of administator objects registered at server, performing server call.

        .. note::
            Objects in the list returned have only basic information. To get full infomation
            use :func:`AVDeskAdmin.retrieve_info()`.

        :return: list of :class:`AVDeskAdmin` instances
        :raises: :class:`AVDeskError` on failure

        Example::

            administrators = av_server.get_administrators()
            for administrator in administrators:
                print 'An administrator with login - %s' % administrator.login
        
        """
        return self._get_list_from_remote('admin')

    def get_repositories(self):
        """Makes request to a server and returns a dictionary with data about repositories used by server.

        :return: list of dictionaries
        :raises: :class:`AVDeskError` on failure

        An extract from repositories data list::
        
            [
                {
                    'state': 'ok',
                    'code': '20-drwwince',
                    'name': 'Mobile Dr.Web AV-Desk Agent',
                    'rev_date_ts': 1311239190,
                    'rev_id': 1311239190
                },
                ...
            ]

        Code sample::

            repositories = av_server.get_repositories()
            for repository in repositories:
                print 'Repository "%s" -> "%s"' % (repository['code'], repository['state'])

        
        """
        return self._structures_list(StructServerRepository, 'get_repositories')

    def _destroy_handle(self):
        """Destroys resource handle if any."""
        if self._handle:
            self._lib_call('dwavdapi_destroy', (self._handle,))


class AVDeskGroup(_AVDeskCommon, _AVDeskShared):
    """AV-Desk group resource class is used to perform groups manipulations.

    :param connector_resource: should be :class:`AVDeskServer` instance.
    :param resource_id: if set server call is performed to get information for resource with given ID.
    :param predefined_handle: if set, resource data could be fetched from a resource at given handle.
    :raises: :class:`AVDeskError` on failure

    """

    _resource_name = 'group'

    def get_statistics(self, ts_from=0, ts_till=0, virus_limit=10):
        """Makes request to a server and returns a dictionary with overall group statistics (including subgroups).

        :param ts_from: timestamp of when statistics starts. If 0 - statistics starts at year 1970. Default 0.
        :param ts_till: timestamp of when staristics ends. If 0 - statistics ends today. Default 0.
        :param virus_limit: virus statistics limiter, to return no more than a given number of viruses. Default 10.
        :return: dictionary
        :raises: :class:`AVDeskError` on failure

        Example::

            stats = group.get_statistics()

        An extract from dictionary returned::

            {
                'viruses': [
                    {
                        'name': 'Trojan.Spambot',
                        'count': 3,
                        'objects_list': [
                            {
                                 'originator': 57,
                                 'originator_text': 'SpIDer Guard G3 for Workstations',
                                 'owner': 'Unknown',
                                  ...
                            },
                            ...
                        ],
                    },
                'scans': {
                    'files': 128,
                    'cured': 28,
                     ...
                },
                'infections': {
                    'ignored': 0,
                    'errors': 0,
                    'deleted': 28,
                     ...
                },
                'stations_total': 1,
                'stations_state': {
                    'unactivated': 0,
                    'deinstalled': 0,
                    'online': 1,
                    ...
                }
            }

        """
        if self.get_resource_id() is None:
            return None

        statistics_struc_ptr = ctypes.c_void_p()
        self._api_call('get_statistics', (self._connector._get_handle(), ctypes.byref(statistics_struc_ptr), self.get_resource_id(), time_t(ts_from), time_t(ts_till), virus_limit))
        statistics = {
            'stations_state': self._get_structure_from_result(StructStationsState, 'statistics_stations_state', [statistics_struc_ptr]).as_dict(),
            'stations_total': self._lib_call('dwavdapi_group_statistics_stations_total', (statistics_struc_ptr,), restype=ctypes.c_ulong),
            'infections': self._get_structure_from_result(StructInfection, 'statistics_infections', [statistics_struc_ptr]).as_dict(),
            'scans': self._get_structure_from_result(StructScan, 'statistics_scans', [statistics_struc_ptr]).as_dict(),
            'viruses': self._structures_list(StructVirus, 'statistics_viruses', handle=statistics_struc_ptr, item_processor=self._get_infected_objects_list),
        }
        self._api_call('statistics_destroy', (statistics_struc_ptr,))

        return statistics

    def type_is_custom(self):
        return bool(self._lib_call(self._api_func_name('is_custom'), (self._get_handle(),), restype=ctypes.c_uint))

    def type_is_platform(self):
        return bool(self._lib_call(self._api_func_name('is_platform'), (self._get_handle(),), restype=ctypes.c_uint))

    def type_is_status(self):
        return bool(self._lib_call(self._api_func_name('is_status'), (self._get_handle(),), restype=ctypes.c_uint))

    def type_is_system(self):
        return bool(self._lib_call(self._api_func_name('is_system'), (self._get_handle(),), restype=ctypes.c_uint))

    def type_is_tariff(self):
        return bool(self._lib_call(self._api_func_name('is_tariff'), (self._get_handle(),), restype=ctypes.c_uint))

    def type_is_transport(self):
        return bool(self._lib_call(self._api_func_name('is_transport'), (self._get_handle(),), restype=ctypes.c_uint))

    def type_is_virtual(self):
        return bool(self._lib_call(self._api_func_name('is_virtual'), (self._get_handle(),), restype=ctypes.c_uint))

    #: This *property* is used to get group statistics. See :func:`get_statistics()`.
    statistics = property(get_statistics)
    #: This *property* is used to verify group is `custom` (artificial).
    is_custom = property(type_is_custom)
    #: This *property* is used to verify group is `platform` virtual group.
    is_platform = property(type_is_platform)
    #: This *property* is used to verify group is `status` virtual group (includes stations Online, Offline, etc.).
    is_status = property(type_is_status)
    #: This *property* is used to verify group is `system` group (not artificial).
    is_system = property(type_is_system)
    #: This *property* is used to verify group is `tariff` group (given that tariffs are groups also).
    is_tariff = property(type_is_tariff)
    #: This *property* is used to verify group is `transport` virtual group (includes stations using TPC/IP, IPX, etc.).
    is_transport = property(type_is_transport)
    #: This *property* is used to verify group is common `virtual` (dynamic group).
    is_virtual = property(type_is_virtual)

    def set_av_component(self, component_id, components_state=AV_COMPONENT_STATES['OPTIONAL']):
        """Sets information about av component for the group.

        :param component_id: component identifier from AV_COMPONENT_IDS.
        :param components_state: component state identifier from AV_COMPONENT_STATES.
        :raises: :class:`AVDeskError` on failure
        """
        self._api_call('set_component', (self._get_handle(), component_id, components_state))

    def get_stations(self, as_id=True):
        """Returns a list of stations in a group, performing a server call.

        :param as_id: boolean. If *True* method returns a list of stations IDs. If *False* - a list
            of :class:`AVDeskStation` objects.
        :return: list
        :raises: :class:`AVDeskError` on failure

        .. warning::
            Setting **as_id** parameter to *False* may lead to considerable server load, since separate server call
            is performed to retrieve full station information.
            One should bear it in mind when querying groups with large amount of stations.

        Example::

            stations = resource_obj.get_stations()
            for id in station:
                print 'Station ID - %s' % id

        """
        station_ids = self._get_list_from_array_simple('stations')
        if as_id:
            return station_ids
        obj_list = []
        for station_id in station_ids:
            obj_list.append(AVDeskStation(self._connector, station_id))
        return obj_list

    def get_subgroups(self, as_id=True):
        """Returns a list of subgroups of a group, performing a server call.

        :param as_id: boolean. If *True* method returns a list of subgroups IDs. If *False* - a list
            of :class:`AVDeskGroup` objects.
        :return: list
        :raises: :class:`AVDeskError` on failure

        .. warning::
            Setting **as_id** parameter to *False* may lead to considerable server load, since separate server call
            is performed to retrieve full group information.
            One should bear it in mind when querying groups with large amount of subgroups.

        Example::

            subgroups = resource_obj.get_subgroups()
            for id in subgroups:
                print 'Subgroup ID - %s' % id

        """
        children_ids = self._get_list_from_array_simple('child_groups')
        if as_id:
            return children_ids
        obj_list = []
        for child_id in children_ids:
            obj_list.append(self.__class__(self._connector, child_id))
        return obj_list

    def get_administrators(self, as_logins=True):
        """Returns a list of administators bound to a group, performing a server call.

        :param as_logins: boolean. If *True* method returns a list of logins. If *False* - a list
            of :class:`AVDeskAdmin` objects.
        :return: list
        :raises: :class:`AVDeskError` on failure

        .. warning::
            Setting **as_logins** parameter to *False* may lead to considerable server load, since separate server call
            is performed to retrieve full administrator information.
            One should bear it in mind when querying groups with large amount of administrators.

        Example::

            administrators = resource_obj.get_administrators()
            for login in administrators:
                print 'An administrator with login - %s' % login

        """
        logins = self._get_list_from_array_simple('admins')
        if as_logins:
            return logins
        obj_list = []
        for login in logins:
            obj_list.append(AVDeskAdmin(self._connector, login))
        return obj_list

    def add_station(self, station_obj):
        """Adds a given station to current group making a server call.
        Creates current group on server if it doesn't already exist.

        :param station_obj: :class:`AVDeskStation` instance
        :return: *True* on success
        :raises: :class:`AVDeskError` on failure

        Example::

            my_station = av_server.new_station('My station')
            saved = group.add_station(my_station)

        """
        if not isinstance(station_obj, AVDeskStation):
            raise AVDeskError('%s is not an AVDeskStation object.' % station_obj)

        if not self._resource_exists:
            self.save()

        station_obj.add_to_groups([self,])
        return station_obj.save()


class AVDeskTariff(AVDeskGroup):
    """AV-Desk tariff group resource class is used to perform tariff groups manipulations.

    :param connector_resource: should be :class:`AVDeskServer` instance.
    :param resource_id: if set server call is performed to get information for resource with given ID.
    :param predefined_handle: if set, resource data could be fetched from a resource at given handle.
    :raises: :class:`AVDeskError` on failure

    """

    def set_grace_period(self, days):
        self._api_call('set_grace_period', (self._get_handle(), days))

    def get_grace_period(self):
        period = self._api_call('grace_period', (self._get_handle(),), restype=ctypes.c_int)
        if period == VAR_UINITIALIZED_NUM:
            period = None
        return period

    #: This *property* is should be an integer from 0 to 99, denoting number of free (no-pay) days included into the tariff.
    grace_period = property(get_grace_period, set_grace_period)

    def get_statistics(self, **kwargs):
        raise NotImplementedError('This feature is unvailable for tariff groups.')
    statistics = property(get_statistics)

    def send_message(self, **kwargs):
        raise NotImplementedError('This feature is unvailable for tariff groups.')

    def create(self, auto_retrieve=True):
        """Performs a server call to create resource with properties defined in object.

        .. note::
            There is a convinience method :func:`save()` to handle both ``create`` and ``update`` operations.

        :param auto_retrieve: boolean to specify whether an additional call
            to server is required after the `create` operation to retrieve
            full resource data. Default: True.
        :return: *True* on success
        :raises: :class:`AVDeskError` on failure

        .. warning::
            Setting ``auto_retrieve`` to False may increase operation performance, but also
            may leave the resource object data in a not up-to-date state. It is advised
            that ``auto_retrieve`` set to False is only used when the resource object
            won't be used further after the operation.

        Example::

            created = tariff.create()

        """
        grp_id = ctypes.c_char_p()
        self._api_call('dwavdapi_tariff_add', (self._connector._get_handle(), self._get_handle(), ctypes.byref(grp_id)))
        grp_id = self._get_string_at_pointer(grp_id)
        if auto_retrieve:
            self.retrieve_info(grp_id)
        self._resource_exists = True
        return True

    def update(self, auto_retrieve=True):
        """Performs server call in attempt to update the resource with information
        from class properties.

        .. note::
            There is a convinience method :func:`save()` to handle both ``create`` and ``update`` operations.

        :param auto_retrieve: boolean to specify whether an additional call
            to server is required after the `update` operation to retrieve
            full resource data. Default: True.
        :return: *True* on success
        :raises: :class:`AVDeskError` on failure

        .. warning::
            Setting ``auto_retrieve`` to False may increase operation performance, but also
            may leave the resource object data in a not up-to-date state. It is advised
            that ``auto_retrieve`` set to False is only used when the resource object
            won't be used further after the operation.

        Example::

            updated = tariff.update()

        """
        self._api_call('dwavdapi_tariff_change', (self._connector._get_handle(), self._get_handle()))
        if auto_retrieve:
            self.retrieve_info()
        self._resource_exists = True
        return True

    def retrieve_info(self, resource_id=None):
        """Performs a server call to retrieve complete resource information by its ID and
        puts it into object's properties.

        :param resource_id: specific ID of the resource. If *None*, ID is taken from the object itself.
        :raises: :class:`AVDeskError` on failure

        Example::

            # resource_obj contains no additional info.
            assert resource_obj.name is None

            # After the following request
            resource_obj.retrieve_info('some_resource_id')

            # resource_obj contains additional info.
            assert resource_obj.name is not None

        """
        if resource_id is None:
            resource_id = self.get_resource_id()
        self._handle = ctypes.c_void_p()
        self._api_call('dwavdapi_tariff_get_info', (self._connector._get_handle(), ctypes.byref(self._handle), resource_id))
        self._resource_exists = True

    def delete(self, stations_move_to=None):
        """Performs a server call in an attempt to delete tariff.

        .. note::
        
            Stations connected to this tariff (if any) should be moved to another tariff group
            (see ``stations_move_to`` parameter).

        .. warning::

            ``stations_move_to`` parameter set to None only works for tariff groups that do not contain any
            stations already.

        :param stations_move_to: tariff ID to move stations to.
        :return: *True* on success
        :raises: :class:`AVDeskError` on failure

        Example::

            deleted = tariff.delete('move_to_tariff_id')

        """
        if isinstance(stations_move_to, AVDeskTariff):
            stations_move_to = stations_move_to.get_resource_id()
        self._api_call('dwavdapi_tariff_delete', (self._connector._get_handle(), self.get_resource_id(), stations_move_to))
        self._resource_exists = False
        return True

    def add_station(self, station_obj):
        """Adds a given station to current tariff group making a server call.
        Creates current tariff group on server if it doesn't already exist.

        :param station_obj: :class:`AVDeskStation` instance
        :return: *True* on success
        :raises: :class:`AVDeskError` on failure

        Example::

            my_station = av_server.new_station('My station')
            saved = tariff.add_station(my_station)

        """
        if not isinstance(station_obj, AVDeskStation):
            raise AVDeskError('%s is not an AVDeskStation object.' % station_obj)

        if not self._resource_exists:
            self.save()

        station_obj.set_tariff(self)
        return station_obj.save()


class AVDeskStation(_AVDeskCommon, _AVDeskGroupable, _AVDeskShared):
    """AV-Desk station resource class is used to perform stations manipulations.

    :param connector_resource: should be :class:`AVDeskServer` instance.
    :param resource_id: if set server call is performed to get information for resource with given ID.
    :param predefined_handle: if set, resource data could be fetched from a resource at given handle.
    :raises: :class:`AVDeskError` on failure

    """

    _resource_name = 'station'

    def get_statistics(self, ts_from=0, ts_till=0, virus_limit=10):
        """Makes request to a server and returns a dictionary with station statistics.

        :param ts_from: timestamp of when statistics starts. If 0 - statistics starts at year 1970. Default 0.
        :param ts_till: timestamp of when staristics ends. If 0 - statistics ends today. Default 0.
        :param virus_limit: virus statistics limiter, to return no more than a given number of viruses. Default 10.
        :return: dictionary
        :raises: :class:`AVDeskError` on failure

        Example::

            stats = station.get_statistics()

        An extract from dictionary returned::

            {
                'viruses': [
                    {
                        'name': 'Trojan.Spambot',
                        'count': 3,
                        'objects_list': [
                            {
                                'originator': 57,
                                 'originator_text': 'SpIDer Guard G3 for Workstations',
                                 'owner': 'Unknown',
                                  ...
                            },
                            ...
                        ],
                    },
                'scans': {
                    'files': 128,
                    'cured': 28,
                     ...
                },
                'infections': {
                    'ignored': 0,
                    'errors': 0,
                    'deleted': 28,
                     ...
                },
                'stations_total': 1,
                'stations_state': {
                    'unactivated': 0,
                    'deinstalled': 0,
                    'online': 1,
                    ...
                }
            }
        
        """
        if self.get_resource_id() is None:
            return None

        statistics_struc_ptr = ctypes.c_void_p()
        self._api_call('get_statistics', (self._connector._get_handle(), ctypes.byref(statistics_struc_ptr), self.get_resource_id(), time_t(ts_from), time_t(ts_till), virus_limit))
        statistics = {
            'infections': self._get_structure_from_result(StructInfection, 'statistics_infections', [statistics_struc_ptr]).as_dict(),
            'scans': self._get_structure_from_result(StructScan, 'statistics_scans', [statistics_struc_ptr]).as_dict(),
            'viruses': self._structures_list(StructVirus, 'statistics_viruses', handle=statistics_struc_ptr, item_processor=self._get_infected_objects_list),
        }
        self._api_call('statistics_destroy', (statistics_struc_ptr,))

        return statistics

    def get_place_data(self):
        """Performs a server call to retrieve station's place information as dictionary.

        :return: dictionary
        :raises: :class:`AVDeskError` on failure

        Example::

            place = station.get_place_data()

        An extract from dictionary returned::

            {
                'province': 'Academgorodok',
                'city': 'Novosibirsk',
                'street': 'Some street',
                'room': None,
                'organization': 'Doctor Web, Ltd.',
                'latitude': 0,
                'longitude': 0,
                'country': 643,
                'floor': None,
                'department': None
            }

        """
        country_id_internal = self._api_call('country', (self._get_handle(),), restype=ctypes.c_int)
        if country_id_internal == -1:
            country_id = None
        else:
            country_id = self._api_call('dwavdapi_country_numcode', (country_id_internal,), restype=ctypes.c_uint)
            
        return {
            'country': country_id,
            'latitude': int(self._api_call('latitude', (self._get_handle(),), restype=ctypes.c_ulong)),
            'longitude': int(self._api_call('longitude', (self._get_handle(),), restype=ctypes.c_ulong)),
            'province': self._api_call('province', (self._get_handle(),), restype=ctypes.c_char_p),
            'city': self._api_call('city', (self._get_handle(),), restype=ctypes.c_char_p),
            'street': self._api_call('street', (self._get_handle(),), restype=ctypes.c_char_p),
            'organization': self._api_call('organization', (self._get_handle(),), restype=ctypes.c_char_p),
            'department': self._api_call('department', (self._get_handle(),), restype=ctypes.c_char_p),
            'room': self._api_call('room', (self._get_handle(),), restype=ctypes.c_char_p),
            'floor': self._api_call('floor', (self._get_handle(),), restype=ctypes.c_char_p),
        }

    def set_place_data(self, country=None, latitude=None, longitude=None, province=None,
                       city=None, street=None, organization=None, department=None, floor=None, room=None):
        """Sets information about station's place.

        :param country: ISO numeric country code integer - (see http://en.wikipedia.org/wiki/ISO_3166-1_numeric)
        :param latitude: Latitude as integer
        :param longitude: Latitude as integer
        :param province: Province name string
        :param city: City name string
        :param street: Street name string
        :param organization: Organization name string
        :param department: Department name string
        :param floor: Floor string
        :param room: Room string

        Example::

            # Selectively set country and organization name for the station.
            station.set_place_data(country=643, organization='Doctor Web, Ltd.')

        """
        for key, value in locals().items():
            if key != 'self':
                if value is not None:
                    self._api_call('set_%s' % key, (self._get_handle(), value))

        if country is not None:
            self._api_call('set_country_by_numcode', (self._get_handle(), country))

    def get_expires_time(self):
        expires = self._api_call('expires_time', (self._get_handle(),), restype=time_t)
        if expires == VAR_UINITIALIZED_NUM:
            return None
        return expires

    def set_expires_time(self, at):
        self._api_call('set_expires_time', (self._get_handle(), time_t(at)))
        return True

    def get_grace_period(self):
        period = self._api_call('grace_period', (self._get_handle(),), restype=ctypes.c_int)
        if period == VAR_UINITIALIZED_NUM:
            period = None
        return period

    def set_tariff(self, id_or_obj):
        """Sets tariff for the current station.

        :param id_or_obj: Tariff resource object or ID.
        :raises: :class:`AVDeskError` on failure

        Example::

            station.set_tariff(tariff_resource_obj)
            # Is equivalent to:
            station.set_tariff('tariff_resource_id')

        """
        if isinstance(id_or_obj, AVDeskTariff):
            id_or_obj = id_or_obj.get_resource_id()
        self._api_call('set_tariff_id', (self._get_handle(), id_or_obj))

    def get_tariff(self, as_id=True):
        """Performs a server call to retrieve a tariff resource for the station.

        :param as_id: boolean. If *True* :class:`AVDeskTariff` object is returned, if *False* - tariff ID
        :return: object or ID. See ``as_id`` parameter.
        :raises: :class:`AVDeskError` on failure

        Example::

            tariff_id = resource_obj.get_tariff()
            print 'Station tariff ID - %s' % tariff_id

        """
        parent = self._api_call('tariff_id', (self._get_handle(),), restype=ctypes.c_char_p)
        if parent is None:
            return None
        if as_id:
            return parent
        parent = AVDeskTariff(self._connector, parent)
        return parent

    def get_last_seen_time(self):
        lastseen = self._api_call('lastseen_time', (self._get_handle(),), restype=ctypes.c_long)
        if lastseen == VAR_UINITIALIZED_NUM:
            return None
        return lastseen

    def get_last_seen_addr(self):
        addr = self._api_call('lastseen_addr', (self._get_handle(),), restype=ctypes.c_char_p)
        if not addr:
            return None
        return addr

    def get_download_url(self):
        return self._get_string_param('url')

    def get_config_url(self):
        return self._get_string_param('config')

    def get_os(self):
        return self._api_call('os_str', (self._get_handle(),), restype=ctypes.c_char_p)

    def get_state(self, as_id=False):
        if as_id:
            return self._api_call('state', (self._get_handle(),), restype=ctypes.c_int)
        else:
            return self._api_call('state_str', (self._get_handle(),), restype=ctypes.c_char_p)

    def set_password(self, password):
        self._api_call('set_password', (self._get_handle(), password))

    def get_password(self):
        return self._get_string_param('password')

    statistics = property(get_statistics)
    place_data = property(get_place_data)
    #: This *property* is used to get and set station's `expires` datetime (as unix timestamp).
    expires_time = property(get_expires_time, set_expires_time)
    #: This *property* is used to get station's grace period (in days) inherited from tariff group.
    grace_period = property(get_grace_period)
    tariff = property(get_tariff, set_tariff)
    #: This *property* is used to get station's last seen unix timestamp.
    last_seen_time = property(get_last_seen_time)
    #: This *property* is used to get station's last seen network address as string.
    last_seen_addr = property(get_last_seen_addr)
    #: This *property* is used to get station's download URL as string.
    download_url = property(get_download_url)
    #: This *property* is used to get station's OS as string.
    os = property(get_os)
    #: This *property* is used to get and station's password.
    password = property(get_password, set_password)
    #: This *property* is used to get station's current state as string (e.g. `online`).
    state = property(get_state)

    def get_av_components_installed(self):
        """Returns a list of antivirus application components installed at the station.

        :return: list of dictionaries with components data
        :raises: :class:`AVDeskError` on failure

        Example::

            installed = station.get_av_components_installed()

        An extract from returned list::

            [
                {
                    'path': 'C:\Program Files\DrWeb AV-Desk',
                    'code': 103,
                    'code_text': 'Dr.Web Microsoft Outlook plugin',
                    'server': 'tcp/94.251.81.210:2193',
                    'installed_ts': 1320062616
                },
                ...
            ]

        """
        structs = self._structures_list(StructStationComponentInstalled, 'components_installed')
        return self._av_item_extend(structs, [], 'dwavdapi_application_name')

    def get_av_components_running(self):
        """Returns a list of antivirus application components running at the station.

        :return: list of dictionaries with components data
        :raises: :class:`AVDeskError` on failure

        Example::

            running = station.get_av_components_running()

        An extract from returned list::

            [
                {
                    'code': 30,
                    'code_text': 'Dr.Web AV-Desk Agent for Windows',
                    'started_ts': 1320523510,
                    'params': None,
                    'user': None,
                    'type': 8
                },
                ...
            ]

        """
        structs = self._structures_list(StructStationComponentRunning, 'components_running')
        return self._av_item_extend(structs, [], 'dwavdapi_application_name')

    def get_av_modules(self):
        """Returns a list of antivirus modules used by the station.

        :return: list of dictionaries with modules data
        :raises: :class:`AVDeskError` on failure

        Example::

            modules = station.get_av_modules()

        An extract from returned list::

            [
                {
                    'hash': '78a61d78e110fbf27975df4a4dc70dfc',
                    'name': 'Dr.Web(c) Scanner for Windows',
                    'created_ts': 1320062617,
                    'modified_ts': 1320062530,
                    'file_name': 'DRWEB32W.EXE',
                    'version': '6.00.11.7112',
                    'file_size': 2299656
                },
                ...
            ]

        """
        structs = self._structures_list(StructModule)
        return structs

    def get_av_bases(self):
        """Returns a list of antivirus bases used by station.

        :return: list of dictionaries with av bases data
        :raises: :class:`AVDeskError` on failure

        Example::

            av_bases = station.get_av_bases()

        An extract from returned list::

            [
                {
                    'file_name': 'drw50001.vdb',
                    'created_ts': 1320059155,
                    'version': '500',
                    'viruses': 24512
                },
                ...
            ]

        """
        return self._structures_list(StructBase, 'bases')

    def get_av_packages(self):
        """Returns a list of antivirus agent download URLs
        for various platforms.

        :return: list of dictionaries with av packages data
        :raises: :class:`AVDeskError` on failure

        Example::

            av_packages = station.get_av_packages()

        An extract from returned list::

            [
                {
                    'url': 'http://localhost/download/download.ds?id=some_id',
                    'type': 1
                },
                ...
            ]

        """
        return self._structures_list(StructPackage, 'packages')

    def get_history(self, ts_from=0, ts_till=0, event_type_filter=None):
        """Performs a server call to retrieve station history information.

        :param ts_from: timestamp of when history starts. If 0 - history starts at year 1970. Default 0.
        :param ts_till: timestamp of when history ends. If 0 - history ends today. Default 0.
        :param event_type_filter: event type identifier (see ``HISTORY_EVENT_TYPES``) to filter history upon.
        :return: list of dictionaries with events data
        :raises: :class:`AVDeskError` on failure

        Example::

            history = station.get_history()

        An extract from returned list::

            [
                {
                    'created_ts': 4294967295,
                    'action_ts': 4294967295,
                    'action_start_ts': 0,
                    'action_finish_ts': 0,
                    'tariff': None,
                    'tariff_name': None,
                    'event_type_id': 5
                },
                ...
            ]

        """
        if event_type_filter is None:
            event_type_filter = -1
        return self._structures_list(StructHistory, 'get_history', handle=self._connector._get_handle(), args_list=[self.id, time_t(ts_from), time_t(ts_till), event_type_filter])

    def get_block_time(self):
        """Returns a tuple with information about station blocking: begin and end unix timestamps.

        :return: list of dictionaries with modules data
        :raises: :class:`AVDeskError` on failure

        Example::

            start_at, finish_at = station.get_block_time()

        """
        begins_at = self._api_call('block_time_begin', (self._get_handle(),), restype=time_t)
        if begins_at == VAR_UINITIALIZED_NUM:
            begins_at = None
        finishes_at = self._api_call('block_time_end', (self._get_handle(),), restype=time_t)
        if finishes_at == VAR_UINITIALIZED_NUM:
            finishes_at = None
        return begins_at, finishes_at

    def set_block_time(self, begin_at, finish_at):
        """Sets blocking information for the station.

        :param begin_at: Block begin unix timestamp
        :param finish_at: Block end unix timestamp
        :return: *True* on success
        :raises: :class:`AVDeskError` on failure

        Example::

            station.set_block_time(start_at, finish_at)

        """
        self._api_call('set_block_time', (self._get_handle(), time_t(begin_at), time_t(finish_at)))
        return True


class AVDeskAdmin(_AVDeskCommon, _AVDeskGroupable):
    """AV-Desk administrator resource class is used to perform manipulations on administrators.

    :param connector_resource: should be :class:`AVDeskServer` instance.
    :param resource_id: if set server call is performed to get information for resource with given ID.
    :param predefined_handle: if set, resource data could be fetched from a resource at given handle.
    :raises: :class:`AVDeskError` on failure

    """

    _resource_name = 'admin'
    _id_callable = 'get_login'

    def set_login(self, login):
        self._api_call('set_login', (self._get_handle(), login))

    def get_login(self):
        return self._get_string_param('login')

    def set_last_name(self, value):
        self._api_call('set_last_name', (self._get_handle(), value))

    def get_last_name(self):
        return self._get_string_param('last_name')

    def set_middle_name(self, value):
        self._api_call('set_middle_name', (self._get_handle(), value))

    def get_middle_name(self):
        return self._get_string_param('middle_name')

    def set_password(self, value):
        self._api_call('set_password', (self._get_handle(), value))

    def get_password(self):
        return self._get_string_param('password')

    def set_readonly(self, value):
        self._api_call('set_readonly', (self._get_handle(), bool(value)))

    def get_readonly(self):
        return self._lib_call(self._api_func_name('is_readonly'), (self._get_handle(),), restype=ctypes.c_bool)

    def type_is_global_admin(self):
        return bool(self._lib_call(self._api_func_name('is_global_admin'), (self._get_handle(),), restype=ctypes.c_uint))

    def type_is_group_admin(self):
        return bool(self._lib_call(self._api_func_name('is_group_admin'), (self._get_handle(),), restype=ctypes.c_uint))

    #: This *property* is used to get or set administarator login.
    login = property(get_login, set_login)
    #: This *property* is used to get or set administarator last name.
    last_name = property(get_last_name, set_last_name)
    #: This *property* is used to get or set administarator middle name.
    middle_name = property(get_middle_name, set_middle_name)
    #: This *property* is used to get or set administarator password.
    password = property(get_password, set_password)
    #: This *property* is used to get or set administarator readonly boolean restriction flag.
    #: If readonly flag is set to True administrator would be unable to perform create/update/delete actions on server resources.
    readonly = property(get_readonly, set_readonly)
    #: This *property* is a boolen used to identify administrator as global (i.e. his powers are not restricted to certain group(s)).
    is_global_admin = property(type_is_global_admin)
    #: This *property* is a boolen used to identify that administrator's powers are restricted to certain group(s).
    is_group_admin = property(type_is_group_admin)

    def create(self, auto_retrieve=True):
        """Performs a server call to create resource with properties defined in object.

        .. note::
            There is a convinience method :func:`save()` to handle both ``create`` and ``update`` operations.

        :param auto_retrieve: boolean to specify whether an additional call
            to server is required after the `update` operation to retrieve
            full resource data. Default: True.
        :return: *True* on success
        :raises: :class:`AVDeskError` on failure

        .. warning::
            Setting ``auto_retrieve`` to False may increase operation performance, but also
            may leave the resource object data in a not up-to-date state. It is advised
            that ``auto_retrieve`` set to False is only used when the resource object
            won't be used further after the operation.

        Example::

            created = resource_obj.create()

        """
        resource_id = ctypes.c_char_p()
        self._api_call('add', (self._connector._get_handle(), self._get_handle(), ctypes.byref(resource_id)))
        if auto_retrieve:
            self.retrieve_info(self.get_login())
        self._resource_exists = True
        return True

    def make_global_admin(self):
        """Shortcut method method that removes the administrator from all groups he is associated with,
        thus making him a global administrator.

        Under the hood it utilizes ``get_groups()`` and ``delete_from_groups()`` methods.

        :return: None
        :raises: :class:`AVDeskError` on failure

        Example::

            my_admin.make_global_admin()

        """
        self.delete_from_groups(self.get_groups())
