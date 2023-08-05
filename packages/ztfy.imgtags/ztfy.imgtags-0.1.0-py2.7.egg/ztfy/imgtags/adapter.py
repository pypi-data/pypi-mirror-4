### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2012 Thierry Florac <tflorac AT ulthar.net>
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


# import standard packages
import chardet
from datetime import datetime
from pyexiv2 import ImageMetadata
from pyexiv2.utils import Fraction, NotifyingList

# import Zope3 interfaces
from zope.app.file.interfaces import IImage

# import local interfaces
from ztfy.imgtags.interfaces import IImageTags, IImageTagString, IImageTagIndexValue, \
                                    IBaseTagInfo, IExifTag, IIptcTag, IXmpTag

# import Zope3 packages
from zope.component import adapts
from zope.interface import implements
from ztfy.utils.timezone import tztime

# import local packages


class ImageTagsAdapter(object):
    """Image tags adapter"""

    adapts(IImage)
    implements(IImageTags)

    def __init__(self, context):
        self.context = context
        self.metadata = ImageMetadata.from_buffer(context.data)
        self.metadata.read()

    def getExifKeys(self):
        return self.metadata.exif_keys

    def getExifTags(self):
        data = self.metadata
        return dict(((tag, data[tag]) for tag in data.exif_keys))

    def getIptcKeys(self):
        return self.metadata.iptc_keys

    def getIptcTags(self):
        data = self.metadata
        return dict(((tag, data[tag]) for tag in data.iptc_keys))

    def getXmpKeys(self):
        return self.metadata.xmp_keys

    def getXmpTags(self):
        data = self.metadata
        return dict(((tag, data[tag]) for tag in data.xmp_keys))

    def getKeys(self):
        data = self.metadata
        return data.exif_keys + data.iptc_keys + data.xmp_keys

    def getTags(self):
        data = self.metadata
        return dict(((tag, data[tag]) for tag in self.getKeys()))

    def getTag(self, key):
        if isinstance(key, (str, unicode)):
            key = (key,)
        for k in key:
            tag = self.metadata.get(k)
            if tag is not None:
                return tag

    def setTag(self, key, value, raw=False):
        if raw:
            self.metadata[key].raw_value = value
        else:
            self.metadata[key].value = value

    def getGPSLocation(self):

        def gpsToWgs(value):
            assert isinstance(value, NotifyingList)
            assert isinstance(value[0], Fraction) and isinstance(value[1], Fraction) and isinstance(value[3], Fraction)
            d0 = value[0].numerator
            d1 = value[0].denominator
            d = float(d0) / float(d1)
            m0 = value[1].numerator
            m1 = value[1].denominator
            m = float(m0) / float(m1)
            s0 = value[2].numerator
            s1 = value[2].denominator
            s = float(s0) / float(s1)
            return d + (m / 60.0) + (s / 3600.0)

        lon = None
        lat = None
        keys = self.getExifKeys()
        if ('Exif.GPSInfo.GPSLongitude' in keys) and \
           ('Exif.GPSInfo.GPSLatitude' in keys):
            lon = gpsToWgs(self.getTag('Exif.GPSInfo.GPSLongitude'))
            if self.getTag('Exif.GPSInfo.GPSLontitudeRef') != 'E':
                lon = -lon
            lat = gpsToWgs(self.getTag('Exif.GPSInfo.GPSLatitude'))
            if self.getTag('Exif.GPSInfo.GPSLatitudeRef') != 'N':
                lat = -lat
        return lon, lat

    def flush(self):
        self.metadata.write()
        self.context.data = self.metadata.buffer


#
# Tags string adapters
#

class DefaultTagStringAdapter(object):
    """Default image tag string adapter"""

    adapts(IBaseTagInfo)
    implements(IImageTagString)

    def __init__(self, context):
        self.context = context

    def toString(self, encoding='utf-8'):
        try:
            return (self.context.name or self.context.key,
                    unicode(str(self.context.value), encoding))
        except:
            encoding = chardet.detect(self.context.value).get('encoding')
            return (self.context.name or self.context.key,
                    unicode(str(self.context.value), encoding))


class ExifTagStringAdapter(object):
    """EXIF tag string adapter"""

    adapts(IExifTag)
    implements(IImageTagString)

    def __init__(self, context):
        self.context = context

    def toString(self, encoding='utf-8'):
        try:
            return (self.context.label or self.context.name or self.context.key,
                    unicode(str(self.context.human_value), encoding))
        except:
            encoding = chardet.detect(self.context.human_value).get('encoding')
            return (self.context.label or self.context.name or self.context.key,
                    unicode(str(self.context.human_value), encoding))


class IptcTagStringAdapter(object):
    """IPTC tag string adapter"""

    adapts(IIptcTag)
    implements(IImageTagString)

    def __init__(self, context):
        self.context = context

    def toString(self, encoding='utf-8'):
        try:
            return (self.context.title or self.context.name or self.context.key,
                    ', '.join((unicode(str(value), encoding) for value in self.context.values)))
        except:
            encoding = chardet.detect(self.context.values[0]).get('encoding')
            return (self.context.title or self.context.name or self.context.key,
                    ', '.join((unicode(str(value), encoding) for value in self.context.values)))


class XmpTagStringAdapter(object):
    """XMP tag string adapter"""

    adapts(IXmpTag)
    implements(IImageTagString)

    def __init__(self, context):
        self.context = context

    def toString(self, encoding='utf-8'):
        try:
            value = str(self.context.value)
        except:
            value = str(self.context.raw_value)
        try:
            return (self.context.title or self.context.name or self.context.key,
                    unicode(value, encoding))
        except:
            encoding = chardet.detect(value).get('encoding')
            return (self.context.title or self.context.name or self.context.key,
                    unicode(value, encoding))


#
# Image tag index value
#

class ImageTagIndexValueAdapter(object):
    """Image tag index value adapter"""

    adapts(IImage)
    implements(IImageTagIndexValue)

    def __init__(self, context):
        self.context = context
        self.tags = IImageTags(context)

    def __getattr__(self, attr):
        tag = self.tags.getTag(attr)
        if tag is not None:
            value = tag.value
            if isinstance(value, datetime) and not value.tzinfo:
                value = tztime(value)
            return value
