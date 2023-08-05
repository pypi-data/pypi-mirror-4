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

import zope.i18nmessageid

import z3c.form.interfaces

import j01.jsonrpc.interfaces

_ = zope.i18nmessageid.MessageFactory('p01')



# j01.jsonrpc forms
class IJ01CriterionForm(j01.jsonrpc.interfaces.IJSONRPCForm):
    """Criterion form."""

    criterionName = zope.schema.Field(
        title=_('Criterion name'),
        description=_('The criterion name'),
        required=True)

    removeCriterionID = zope.schema.Field(
        title=u'Remove criterion element ID',
        description=u'Remove criterion element ID',
        required=True)

    removeCriterionLabel = zope.schema.Field(
        title=u'Remove criterion label',
        description=u'Remove criterion label',
        required=True,)

    def save():
        """Save criterion changes."""

    def removeJavaScript():
        """Javascriptwith which will apply the remove code to the remove link.
        """


class IJ01SearchPage(j01.jsonrpc.interfaces.IJSONRPCPage):
    """Search page"""

    criterionRows = zope.schema.List(
        title=_('List of criterion forms'),
        description=_('A list of criterion forms'),
        value_type=zope.schema.Field(
            title=_('Criterion form'),
            description=_('Criterion form'),
            required=True
            ),
        default=[],
        required=False)

    rowName = zope.schema.Field(
        title=u'Row name',
        description=u'The row name used for lookup row forms',
        default='j01CriterionForm',
        required=True)

    addCriterionName = zope.schema.Field(
        title=u'Add criterion name',
        description=u'Add criterion name',
        required=True)

    removeCriterionName = zope.schema.Field(
        title=u'Remove criterion name',
        description=u'Remove criterion name',
        required=True)

    criterionFactories = zope.schema.Dict(
        title=_(u'Name criterion factory dictionary'),
        description=_(u'Name criterion factory dictionary'),
        required=True,
        default={})

    searchFilter = zope.schema.Field(
        title=_('Search filter'),
        description=_('The search filter'),
        required=False)

    def createSearchFilter():
        """Create SearchFilter"""

    def getSearchFilters():
        """Returns a list of persistent stored search filters"""

    def addSearchFilter(name, searchFilter):
        """Add SearchFilter to mongodb
        
        Used by FilterSaveDialog doHandleSaveFilter for get SearchFilter from
        session and store them in mongodb

        """

    def loadSearchFilter(key):
        """Load SearchFilter from mongodb
        
        Used by FilterLoadDialog doHandleLoadFilter for get SearchFilter from
        mongodb and loaed them into session

        """

    def removeSearchFilter(key):
        """Remove SearchFilter from mongodb
        
        Used by FilterLoadDialog doHandleRemoveFilter

        """

    def saveFilterData():
        """Save new or update filter session data"""

    def resetValues():
        """Knows how to reset the search result after loading a new filter"""

    def setupCriterionRows():
        """Setup criterion row forms."""

    def renderFilter():
        """Render filter form"""


class IJ01SearchForm(IJ01SearchPage, j01.jsonrpc.interfaces.IJSONRPCForm):
    """Search form"""


class IConnectorWidget(z3c.form.interfaces.IRadioWidget):
    """Connector widget with special template."""
    