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

# import Zope3 interfaces

# import local interfaces

# import Zope3 packages
from zope.interface import Interface, Attribute

# import local packages

from ztfy.imgtags import _


#
# Pyexiv2 tags interfaces
#

class IBaseTagInfo(Interface):
    """Base pyexiv2 tag interface"""
    key = Attribute(_("Tag key code"))
    name = Attribute(_("Tag name"))
    description = Attribute(_("Tag description"))
    type = Attribute(_("Tag type"))

class IBaseTagWriter(Interface):
    """Base pyexiv2 tag writer interface"""
    value = Attribute(_("Tag value"))
    raw_value = Attribute(_("Tag raw value"))


class IExifTagInfo(IBaseTagInfo):
    """Base pyexiv2 EXIF tag interface"""
    label = Attribute(_("Tag label"))
    section_name = Attribute(_("Section name"))
    section_description = Attribute(_("Section description"))
    human_value = Attribute(_("Tag human value"))

    def contents_changed(self):
        """Check if tag contents changed"""

class IExifTagWriter(IBaseTagWriter):
    """Base pyexiv2 EXIF tag writer interface"""

class IExifTag(IExifTagInfo, IExifTagWriter):
    """Pyexiv2 EXIF tag interface"""


class IIptcTagInfo(IBaseTagInfo):
    """Base pyexiv2 IPTC tag interface"""
    title = Attribute(_("Tag title"))
    photoshop_name = Attribute(_("Photoshop name"))
    record_name = Attribute(_("Tag record name"))
    record_description = Attribute(_("Tag record description"))
    repeatable = Attribute(_("Repeatable tag ?"))

    def contents_changed(self):
        """Check if tag contents changed"""

class IIptcTagWriter(IBaseTagWriter):
    """Base pyexiv2 IPTC tag writer interface"""
    values = Attribute(_("Tag values"))
    raw_values = Attribute(_("Tag raw values"))

class IIptcTag(IIptcTagInfo, IIptcTagWriter):
    """Pyexiv2 IPTC tag interface"""


class IXmpTagInfo(IBaseTagInfo):
    """Base pyexiv2 XMP tag interface"""
    title = Attribute(_("Tag title"))

class IXmpTagWriter(IBaseTagWriter):
    """Base pyexiv2 XMP tag writer interface"""

class IXmpTag(IXmpTagInfo, IXmpTagWriter):
    """Pyexiv2 XMP tag interface"""


#
# Images tags interfaces
#

class IImageTags(Interface):
    """Image tags interface"""

    metadata = Attribute(_("Raw metadata"))

    def getExifKeys(self):
        """Get keys of used EXIF tags"""

    def getExifTags(self):
        """Get key/tag dict of used EXIF tags"""

    def getIptcKeys(self):
        """Get keys of used IPTC tags"""

    def getIptcTags(self):
        """Get key/tag dict of used IPTC tags"""

    def getXmpKeys(self):
        """Get keys of used XMP tags"""

    def getXmpTags(self):
        """Get key/tag dict of used XMP tags"""

    def getKeys(self):
        """Get keys of all used tags"""

    def getTags(self):
        """Get key/tag dict of all used tags"""

    def getTag(self, key):
        """Get tag for given key
        
        Key can also be a list or tuple, in which case given tags are
        checked until one of them is not null
        """

    def setTag(self, key, value, raw=False):
        """Set value of given tag"""

    def getGPSLocation(self):
        """Get GPS coordinates in WGS84 projection system"""

    def flush(self):
        """Write modified tags to image"""


class IImageTagString(Interface):
    """Image tag string representation interface"""

    def toString(self, encoding='utf-8'):
        """Render tag as string
        
        Returns a tuple containing tag name and tag value
        """


#
# Image tag index interface
#

class IImageTagIndexValue(Interface):
    """Get index value for a given tag"""

    def __getattr__(self, attr):
        """Get indexed value for given tag"""
