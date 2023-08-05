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

from z3c.form.interfaces import IFileWidget


class IFSFileUploadWidget(IFileWidget):
    """Widget for IFSFileUpload field.

    The used FSFileUploadDataConverter for this widget returns an
    FSFile pointing to the used temp file path.
    """


class IZODBFileUploadWidget(IFileWidget):
    """Widget for IBytes field.

    The used ZODBFileUploadDataConverter for this widget can read the file
    data from our temp file and return this data as content.
    """
