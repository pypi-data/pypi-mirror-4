##############################################################################
#
# Copyright (c) 2011 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id:$
"""
__docformat__ = "reStructuredText"

import datetime
import pygeoip
import pytz
import zope.interface

from p01.geo import interfaces

import os.path

loaded_locator = None

def get_loaded_locator(path={'db':None,'tzdb':None}):
    """
    Return a GeoLocator with the DBs loaded.
    """
    global loaded_locator
    if loaded_locator is None:
        basepath = os.path.join(os.path.dirname(__file__), 'data')
        db = path['db'] or os.path.join(basepath, 'GeoLiteCity.dat')
        tzdb = path['tzdb'] or os.path.join(basepath, 'timezone.txt')
        loaded_locator = GeoLocator(db, tzdb)
    return loaded_locator


class GeoData(object):
    """GeoLocator data"""

    zope.interface.implements(interfaces.IGeoData)

    ip = None
    countryCode = None
    countryCode3 = None
    countryName = None
    regionName = None
    metroCode = None
    city = None
    timezone = None
    longitude = None
    latitude = None
    postalCode = None

    def __init__(self, ip, data):
        self.ip = ip
        # data is a dict as returned by pygeoip.record_by_addr()
        self.countryCode = data.get('country_code')
        self.countryCode3 = data.get('country_code3')
        self.countryName = data.get('country_name')
        self.regionName = data.get('region_name')
        self.metroCode = data.get('metro_code')
        self.city = data.get('city')
        self.timezone = data.get('time_zone')
        self.longitude = data.get('longitude')
        self.latitude = data.get('latitude')
        self.postalCode = data.get('postal_code')

    def __repr__(self):
        return '<%s for %s>' %(self.__class__.__name__, self.ip)


class Cache(object):
    INVALIDATE_TIMEOUT = datetime.timedelta(days=1)

    def __init__(self):
        self.data = {}

    def lookup(self, key):
        try:
            valid_until, value = self.data[key]
            if valid_until > datetime.datetime.now():
                return value
            else:
                self.invalidate(key)
                return None
        except KeyError:
            return None

    def put(self, key, value):
        valid_until = datetime.datetime.now()+self.INVALIDATE_TIMEOUT
        self.data[key] = (valid_until, value)

    def invalidate(self, key):
        try:
            del self.data[key]
        except:
            pass

    def clear(self):
        self.data.clear()

class CacheForever(object):
    def __init__(self):
        self.data = {}

    def lookup(self, key):
        try:
            return self.data[key]
        except KeyError:
            return None

    def put(self, key, value):
        self.data[key] = value

    def invalidate(self, key):
        try:
            del self.data[key]
        except:
            pass

    def clear(self):
        self.data.clear()


class TimeZoneDB(object):
    def __init__(self, path):
        data = {}
        first = True
        for line in open(path, 'r'):
            if first:
                first = False
                continue
            (country, region, tzName) = line.strip().split('\t')
            tz = pytz.timezone(tzName)
            data[(country, region)] = tz

        self.data = data

    def lookup(self, country, region):
        if region is None:
            region = ''
        tz = self.data.get((country, region))
        if tz is None:
            tz = self.data.get((country, ''))
        return tz

class GeoLocator(object):
    """GeoLocator instance"""

    zope.interface.implements(interfaces.IGeoLocator)

    def __init__(self, DBpath, TZpath):
        # load geo locator data
        self._geodb = pygeoip.GeoIP(DBpath, pygeoip.STANDARD)
        self._timezonedb = TimeZoneDB(TZpath)
        self._cacheData = CacheForever()
        self._cacheTZ = CacheForever()

    def getData(self, ip):
        obj = self._cacheData.lookup(ip)
        if obj is None:
            data = self._geodb.record_by_addr(ip)
            if data is None:
                obj = None
            else:
                tz = self._timezonedb.lookup(data['country_code'],
                                             data.get('region_name'))
                data['time_zone'] = tz
                obj = GeoData(ip, data)
            self._cacheData.put(ip, obj)
        return obj

    def getTimeZone(self, ip):
        tz = self._cacheTZ.lookup(ip)
        if tz is None:
            try:
                # region_by_addr burps on invalid IPs
                data = self._geodb.region_by_addr(ip)
            except TypeError:
                data = None
            if data is None:
                tz = None
            else:
                tz = self._timezonedb.lookup(data['country_code'],
                                             data.get('region_name'))
            self._cacheTZ.put(ip, tz)
        return tz
