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


import ctypes
import sys
import logging

time_t = ctypes.c_long
if sys.platform == 'win32':
    time_t = ctypes.c_int64


class AVDStruct(ctypes.Structure):
    """Basic class for information structures with helper methods defined.
    Essentially prototupes of all the structures defined in this module could be found
    in `libdwavdapi` headers files.

    """

    def __str__(self):
        """Helps to print out structure data."""
        return '%s' % self.as_dict()

    def as_dict(self):
        """Converts structure into a dictionary."""
        output = {}
        for field, ftype in self._fields_:
            data = getattr(self, field)
            logging.debug('FIELD: %s. TYPE: %s. DATA: %s'  % (field, ftype, data))
            if issubclass(ftype, AVDStruct):
                data = data.as_dict()
            output[field] = data
        return output


class StructMessage(AVDStruct):
    """Holds message data."""
    _fields_ = [
        ('message', ctypes.c_char_p),
        ('url_text', ctypes.c_char_p),
        ('url', ctypes.c_char_p),
        ('logo', ctypes.c_char_p),
        ('logo_url', ctypes.c_char_p),
        ('logo_text', ctypes.c_char_p),
    ]


class StructServer(AVDStruct):
    """Holds basic information about AV-Desk server."""
    _fields_ = [
        ('version', ctypes.c_char_p),
        ('branch', ctypes.c_char_p),
        ('api_version', ctypes.c_char_p),
        ('api_build', ctypes.c_char_p),
        ('uuid', ctypes.c_char_p),
        ('platform', ctypes.c_char_p),
        ('os', ctypes.c_char_p),
        ('host', ctypes.c_char_p),
        ('uptime', ctypes.c_ulong),
        ('groups_total', ctypes.c_ulong),
        ('groups_custom', ctypes.c_ulong),
        ('groups_system', ctypes.c_ulong),
        ('tariffs_total', ctypes.c_ulong),
        ('stations_total', ctypes.c_ulong),
        ('stations_licensed', ctypes.c_ulong),
        ('stations_available', ctypes.c_ulong),
    ]


class StructServerKey(AVDStruct):
    """Holds information about AV-Desk server key."""
    _fields_ = [
        ('md5', ctypes.c_char_p),
        ('uuid', ctypes.c_char_p),
        ('dealer_name', ctypes.c_char_p),
        ('user_name', ctypes.c_char_p),
        ('sn', ctypes.c_char_p),
        ('created_ts', time_t),
        ('expires_ts', time_t),
        ('activated_ts', time_t),
        ('products', ctypes.c_ulong),
        ('clients', ctypes.c_ulong),
        ('user', ctypes.c_ulong),
        ('servers', ctypes.c_ulong),
        ('dealer', ctypes.c_ulong),
        ('antispam', ctypes.c_uint),
    ]


class StructInfection(AVDStruct):
    """Holds infections statistics."""
    _fields_ = [
        ('deleted', ctypes.c_ulong),
        ('cured', ctypes.c_ulong),
        ('incurable', ctypes.c_ulong),
        ('moved', ctypes.c_ulong),
        ('locked', ctypes.c_ulong),
        ('renamed', ctypes.c_ulong),
        ('errors', ctypes.c_ulong),
        ('ignored', ctypes.c_ulong),
        ('total', ctypes.c_ulong),
    ]


class StructScan(AVDStruct):
    """Holds scans statistics."""
    _fields_ = [
        ('infected', ctypes.c_ulong),
        ('deleted', ctypes.c_ulong),
        ('moved', ctypes.c_ulong),
        ('cured', ctypes.c_ulong),
        ('errors', ctypes.c_ulong),
        ('renamed', ctypes.c_ulong),
        ('locked', ctypes.c_ulong),
        ('size', ctypes.c_double),
        ('files', ctypes.c_double),
    ]


class StructStationsState(AVDStruct):
    """Holds stations states statistics."""
    _fields_ = [
        ('online', ctypes.c_ulong),
        ('deinstalled', ctypes.c_ulong),
        ('blocked', ctypes.c_ulong),
        ('expired', ctypes.c_ulong),
        ('offline', ctypes.c_ulong),
        ('activated', ctypes.c_ulong),
        ('unactivated', ctypes.c_ulong),
        ('total', ctypes.c_ulong),
    ]


class StructServerTraffic(AVDStruct):
    """Holds AV-Desk server traffic statistics."""
    _fields_ = [
        ('in', ctypes.c_double),
        ('out', ctypes.c_double),
        ('total', ctypes.c_double),
    ]


class StructKey(AVDStruct):
    """Holds key information for groups and stations."""
    _fields_ = [
        ('inherited_group_id', ctypes.c_char_p),
        ('key', ctypes.c_char_p),
    ]


class StructInfectionObject(AVDStruct):
    """Holds infection object information."""
    _fields_ = [
        ('path', ctypes.c_char_p),
        ('owner', ctypes.c_char_p),
        ('username', ctypes.c_char_p),
        ('station_uuid', ctypes.c_char_p),
        ('originator', ctypes.c_uint),
        ('treatment', ctypes.c_uint),
        ('object_type_id', ctypes.c_uint),
        ('infection_type_id', ctypes.c_uint),
    ]


class StructVirus(AVDStruct):
    """Holds AV-Desk virus information."""
    _fields_ = [
        ('name', ctypes.c_char_p),
        ('objects_list', ctypes.POINTER(StructInfectionObject)),
        ('count', ctypes.c_ulong),
    ]


class StructServerRepository(AVDStruct):
    """Holds AV-Desk repository information."""
    _fields_ = [
        ('code', ctypes.c_char_p),
        ('state', ctypes.c_char_p),
        ('name', ctypes.c_char_p),
        ('rev_date_ts', time_t),
        ('rev_id', ctypes.c_uint),
    ]


class StructStationComponentInstalled(AVDStruct):
    """Holds AV-Desk antivirus component installed on station information."""
    _fields_ = [
        ('path', ctypes.c_char_p),
        ('server', ctypes.c_char_p),
        ('installed_ts', time_t),
        ('code', ctypes.c_uint),
    ]


class StructStationComponentRunning(AVDStruct):
    """Holds AV-Desk antivirus component running on station information."""
    _fields_ = [
        ('user', ctypes.c_char_p),
        ('params', ctypes.c_char_p),
        ('started_ts', time_t),
        ('code', ctypes.c_uint),
        ('type', ctypes.c_uint),
    ]


class StructBase(AVDStruct):
    """Holds AV-Desk antivirus base information."""
    _fields_ = [
        ('file_name', ctypes.c_char_p),
        ('version', ctypes.c_char_p),
        ('created_ts', time_t),
        ('viruses', ctypes.c_uint),
    ]

class StructPackage(AVDStruct):
    """Holds AV-Desk antivirus agent packages information."""
    _fields_ = [
        ('url', ctypes.c_char_p),
        ('type', ctypes.c_uint),
        ]

class StructHistory(AVDStruct):
    """Holds AV-Desk station history information."""
    _fields_ = [
        ('tariff', ctypes.c_char_p),
        ('tariff_name', ctypes.c_char_p),
        ('created_ts', time_t),
        ('action_ts', time_t),
        ('action_start_ts', time_t),
        ('action_finish_ts', time_t),
        ('event_type_id', ctypes.c_int),
    ]


class StructModule(AVDStruct):
    """Holds AV-Desk station module information."""
    _fields_ = [
        ('file_name', ctypes.c_char_p),
        ('hash', ctypes.c_char_p),
        ('name', ctypes.c_char_p),
        ('version', ctypes.c_char_p),
        ('created_ts', time_t),
        ('modified_ts', time_t),
        ('file_size', ctypes.c_double),
    ]


class StructComponent(AVDStruct):
    """Holds AV-Desk antivirus component information."""
    _fields_ = [
        ('parent_group_id', ctypes.c_char_p),
        ('code', ctypes.c_uint),
        ('status', ctypes.c_uint),
    ]


class StructRight(AVDStruct):
    """Holds AV-Desk right information."""
    _fields_ = [
        ('parent_group_id', ctypes.c_char_p),
        ('code', ctypes.c_uint),
        ('status', ctypes.c_uint),
    ]
