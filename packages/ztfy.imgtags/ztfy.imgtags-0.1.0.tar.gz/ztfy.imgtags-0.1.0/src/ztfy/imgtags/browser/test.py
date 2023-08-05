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
from persistent import Persistent

# import Zope3 interfaces

# import local interfaces
from ztfy.imgtags.interfaces import IImageTags

# import Zope3 packages
from z3c.form import field
from zope.container.contained import Contained
from zope.interface import implements, Interface
from zope.schema import TextLine
from zope.schema.fieldproperty import FieldProperty
from zope.traversing.browser.absoluteurl import absoluteURL

# import local packages
from ztfy.extfile.blob import BlobImage
from ztfy.file.property import ImageProperty
from ztfy.file.schema import ImageField
from ztfy.skin.form import AddForm, EditForm, DisplayForm
from ztfy.skin.menu import MenuItem

from ztfy.imgtags import _


class IImageTagsTest(Interface):
    """Image tags test interface"""

    title = TextLine(title=u"Title", required=True)
    image = ImageField(title=_("Image data"), required=True)


class ImageTagsTest(Persistent, Contained):
    """Image tags test class"""

    implements(IImageTagsTest)

    title = FieldProperty(IImageTagsTest['title'])
    image = ImageProperty(IImageTagsTest['image'], klass=BlobImage)


class ImageTagsTestAddFormMenuItem(MenuItem):
    """Image tags test add menu item"""
    title = ":: Add image tags test..."


class ImageTagsTestAddForm(AddForm):
    """Image tags test add form"""

    fields = field.Fields(IImageTagsTest)

    def create(self, data):
        img = ImageTagsTest()
        img.title = data.get('title')
        return img

    def add(self, object):
        self.context[object.title] = object

    def nextURL(self):
        return '%s/@@contents.html' % absoluteURL(self.context, self.request)


class ImageTagsTestEditForm(EditForm):
    """Image tags test edit form"""

    fields = field.Fields(IImageTagsTest)


class ImageTagsTestTagsDisplayFormMenuItem(MenuItem):
    """Image tags test add menu item"""
    title = "EXIF/IPTC/XMP tags"


class ImageTagsTestTagsDisplayForm(DisplayForm):
    """Image tags test tags display form"""

    fields = field.Fields(Interface)

    @property
    def tags(self):
        return IImageTags(self.context.image)
