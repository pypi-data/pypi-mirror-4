##############################################################################
#
# Copyright (c) 2008 Projekt01 GmbH and Contributors.
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
import zope.component
import zope.schema.interfaces

from z3c.form import widget
import z3c.form.browser.file
from z3c.form.interfaces import IFieldWidget

import p01.fsfile.schema
from p01.fswidget import interfaces
from p01.fswidget import layer


# widget for file system file based file
class FSFileUploadWidget(z3c.form.browser.file.FileWidget):
    """Widget for IFSFileUpload field.

    The registered FSFileUploadDataConverter for this widget returns an
    FSFile pointing to the given temp file path.
    """

    zope.interface.implementsOnly(interfaces.IFSFileUploadWidget)

    klass = u'fsFileUploadWidget'
    css = u'file'


@zope.component.adapter(p01.fsfile.schema.IFSFileUpload,
                        layer.IFSWidgetBrowserLayer)
@zope.interface.implementer(IFieldWidget)
def FSFileUploadFieldWidget(field, request):
    """IFieldWidget factory for FSFileUploadWidget."""
    return widget.FieldWidget(field, FSFileUploadWidget(request))


# widget for default zope.schema.interfaces.IBytes field
class ZODBFileUploadWidget(z3c.form.browser.file.FileWidget):
    """Widget for IBytes field.

    The registered FileUploadDataConverter for this widget can read the file
    data from our temp file.
    """

    zope.interface.implementsOnly(interfaces.IZODBFileUploadWidget)

    klass = u'fileUploadWidget'
    css = u'file'


@zope.component.adapter(zope.schema.interfaces.IBytes,
                        layer.IFSWidgetBrowserLayer)
@zope.interface.implementer(IFieldWidget)
def ZODBFileUploadFieldWidget(field, request):
    """IFieldWidget factory for FileUploadWidget."""
    return widget.FieldWidget(field, ZODBFileUploadWidget(request))
