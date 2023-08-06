##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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

import z3c.form.interfaces
import z3c.form.widget
import z3c.form.browser.radio

from j01.searcher import interfaces


class ConnectorWidget(z3c.form.browser.radio.RadioWidget):
    """Connector widget"""
    zope.interface.implementsOnly(interfaces.IConnectorWidget)

    klass = u'connector-widget'


@zope.component.adapter(zope.schema.interfaces.IField,
                        z3c.form.interfaces.IFormLayer)
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def getConnectorWidget(field, request):
    """IFieldWidget factory for ConnectorWidget."""
    return z3c.form.widget.FieldWidget(field, ConnectorWidget(request))