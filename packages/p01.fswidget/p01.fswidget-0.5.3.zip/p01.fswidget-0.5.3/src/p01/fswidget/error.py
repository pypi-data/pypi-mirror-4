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

import p01.fsfile.exceptions

import z3c.form.error


class FSFileProcessingErrorViewSnippet(z3c.form.error.ErrorViewSnippet):
    """An error view for ValueError."""
    zope.component.adapts(p01.fsfile.exceptions.FSFileProcessingError, None,
        None, None, None, None)

    def createMessage(self):
        return self.error.args[0]