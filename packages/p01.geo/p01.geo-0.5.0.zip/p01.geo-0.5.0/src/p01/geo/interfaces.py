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

import zope.interface
import zope.schema


class IGeoData(zope.interface.Interface):
    """GeoLocator"""
    ip = zope.schema.TextLine(title=u"IP address")
    countryCode = zope.schema.TextLine(title=u"Country code")
    countryCode3 = zope.schema.TextLine(title=u"Country code")
    countryName = zope.schema.TextLine(title=u"Country name")
    regionName = zope.schema.TextLine(title=u"Region name")
    metroCode = zope.schema.TextLine(title=u"Metro code")
    city = zope.schema.TextLine(title=u"City")
    timezone = zope.interface.Attribute("pytz timezone")
    longitude = zope.schema.Float(title=u"Longitude")
    latitude = zope.schema.Float(title=u"Latitude")
    postalCode = zope.schema.TextLine(title=u"Postal code")


class IGeoLocator(zope.interface.Interface):
    """GeoLocator, all lookup values are cached"""

    def getTimeZone(ip):
        """Return a pytz timezone based on IP"""

    def getData(ip):
        """Return an instance of IGeoData based on IP"""