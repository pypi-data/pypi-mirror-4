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

import zope.component
import zope.schema.interfaces
import zope.i18nmessageid

import z3c.form.interfaces
import z3c.form.converter

from p01.tmp.interfaces import ITMPFile
from p01.fsfile.interfaces import IFSStorage
from p01.fsfile.schema import IFSFileUpload
from p01.fswidget import interfaces

_ = zope.i18nmessageid.MessageFactory('p01')


def extractFileName(filename, allowEmptyPostfix=False):
    if not allowEmptyPostfix:
        # Uploads from win/IE need some cleanup because the filename
        # includes also the path.
        filename = filename.replace('\\', '/')  # make it uniform across win/linux
        filename = filename.replace(':', '/')  # and mac
        # We need to strip out the path section even if we do not remove them
        # later, because we just need to check the filename extension.
        filename = filename.split('/')[-1]

    if not allowEmptyPostfix:
        dottedParts = filename.split('.')
        if len(dottedParts) <= 1:
            raise ValueError(_('Missing filename extension.'))
    return filename


class FSFileUploadDataConverter(z3c.form.converter.BaseDataConverter):
    """A special data converter for bytes, supporting also FileUpload.

    This converter knows how to create a FSFile based on the given temp file
    path.
    """
    zope.component.adapts(IFSFileUpload, z3c.form.interfaces.IWidget)

    def toWidgetValue(self, value):
        """See interfaces.IDataConverter"""
        return u''

    def toFieldValue(self, value):
        """We check if we already got a temp file or we create one.

        Moving the file to it's correct location is done by the configurator.
        Make sure that the object which implements the file provides IFSFile.
        This will make sure that the configurator is available.

        Note: it's very important that you use a tempfile.mkstemp file and not
        a os system file handle. The later get removed after closing the python
        thread even if we moved the file to it's new location.

        """
        if value is None or value == '':
            return self.field.missing_value

        if hasattr(value, 'tmpFile') and ITMPFile.providedBy(value.tmpFile):
            # get storage based on fields fsStorageName value
            fsStorageName = self.field.fsStorageName
            fsNameSpace = self.field.fsNameSpace
            fsFileFactory = self.field.fsFileFactory
            fsStorage = zope.component.getUtility(IFSStorage, fsStorageName)
            # extract filename
            fileName = extractFileName(value.filename,
                self.field.allowEmptyPostfix)
            return fsStorage.store(value.tmpFile, fileName, fsNameSpace,
                fsFileFactory)
        else:
            # should never happen
            raise ValueError('No TMPFileUpload given.')


# TODO: implement default ZODB IBytes based file upload widget
class ZODBFileUploadDataConverter(z3c.form.converter.BaseDataConverter):
    """A special data converter for bytes, supporting our temp file concept.

    This converter knows how to convert the temp file into a data stream.
    """
    zope.component.adapts(zope.schema.interfaces.IBytes,
                          interfaces.IZODBFileUploadWidget)

    def toWidgetValue(self, value):
        """See interfaces.IDataConverter"""
        return u''

    def toFieldValue(self, value):
        """Convert given temp file into IBytes field conform data. --> str"""
        if value is None or value == '':
            # When no new file is uploaded, send a signal that we do not want
            # to do anything special.
            return z3c.form.interfaces.NOT_CHANGED

        if hasattr(value, 'tmpFile') and ITMPFile.providedBy(value.tmpFile):
            return value.tmpFile.read()
        else:
            # should never happen
            raise ValueError('No TMPFileUpload given.')
