###############################################################################
#
# Copyright (c) 2012 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
###############################################################################
"""
$Id: __init__.py 2798 2012-03-04 02:29:53Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.component

from z3c.form import widget
import z3c.form.browser.file
from z3c.form.interfaces import IFieldWidget

import m01.fs.schema
import m01.fs.layer
from m01.fs import interfaces


# z3c.from
class FileUploadWidget(z3c.form.browser.file.FileWidget):
    """Widget for IFileUpload field.

    The registered FileUploadDataConverter for this widget returns an
    FileUpload item
    """

    zope.interface.implementsOnly(interfaces.IFileUploadWidget)

    css = u'fsFileUploadWidget'


@zope.component.adapter(m01.fs.schema.IFileUpload,
                        m01.fs.layer.IFileUploadWidgetLayer)
@zope.interface.implementer(IFieldWidget)
def FileUploadFieldWidget(field, request):
    """IFieldWidget factory for FileUploadWidget."""
    return widget.FieldWidget(field, FileUploadWidget(request))
